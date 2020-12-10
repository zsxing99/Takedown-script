"""
FindRepoTask
--------------------------------------------------
Run tool to find repos that should be taken down
    1. Tool should group repos by owner, if one owner has multiple repos in violation
    2. Newly found repos are tagged as “new”
"""

from .BaseTask import BaseTask
from takedown.client.GitHub import GitHubClient
import sys
import requests
import datetime


class FindRepoTask(BaseTask):

    def __init__(self, **config):
        super().__init__(**config)
        self.__dict__.update(config)
        self.client = GitHubClient()
        self.__token = ""
        self.__is_authenticated = False
        self.search_query = ""
        self.previous_records = None
        # save rate limit and bandwidth with GitHub requests, cache user_info
        self.cached_user_info = {}

    def prepare(self, token: str, search_query: str, previous_records: dict = None):
        """
        prepare the task
        :param token: input github token
        :param search_query: input search_query
        :param previous_records: previous records of searched repos
        :return: self instance
        """
        self.client.authenticate(token)
        self.__token = token
        self.__is_authenticated = True
        self.search_query = search_query
        self.previous_records = previous_records
        return self

    def __pre_check__(self, ignore_warning: bool = False):
        """
        run before execute
        :return: false if check failed
        """
        if self.search_query == "":
            return False
        if len(self.search_query) < 5 and not ignore_warning:
            confirm = None
            while not confirm:
                confirm = input("The length of search query `{}` is too short that will produce massive search results."
                                " Are you sure to proceed? [y/n]\n".format(self.search_query))
                if confirm.lower() not in ['y', 'n']:
                    confirm = None
                    print("Please enter 'y' or 'n': ")
                elif confirm.lower() == 'n':
                    return False
        if not self.__is_authenticated:
            print("No token provided for GitHub client.", file=sys.stderr)
            return False
        return True

    def execute_search_by_code(self, ignore_warning: bool = False, chain: bool = False):
        """
        search by code
        :param chain: true if used in multiple targets
        :param ignore_warning:
        :return:
        """
        # pre-check
        if not self.__pre_check__(ignore_warning):
            return None

        # try to fire one request
        print("Start searching for code...")
        first_result = self.client.search(self.search_query, "code", )
        if not first_result:
            print("An error occurs, abort program", file=sys.stderr)
            return None
        else:
            print("Results retrieved from GitHub. Page: 1.")
        if first_result.total > 500 and not ignore_warning:
            confirm = None
            while not confirm:
                confirm = input("The number of search results is {}. It is so large that you may narrow search queries."
                                " The max retrievable number is 1000. Are you sure to proceed? [y/n]\n"
                                .format(first_result.total))
                if confirm.lower() not in ['y', 'n']:
                    confirm = None
                    print("Please enter 'y' or 'n': ")
                elif confirm.lower() == 'n':
                    return None

        fields_filtered_results = []
        code_search_result = first_result
        total = first_result.total
        page = 2  # page 1 has been requested
        while total > (page - 1) * 100 and page <= 10:
            fields_filtered_results = [*code_search_result.generate_list([
                "owner__url", "repo__name", "repo__html_url",
            ]), *fields_filtered_results]
            code_search_result = self.client.search(self.search_query, "code", page=page)
            if not code_search_result:
                print("Error in search with GitHub rest APIs", file=sys.stderr)
                return None
            else:
                print("Results retrieved from GitHub. Page: {}.".format(page))
            page += 1
        fields_filtered_results = [*code_search_result.generate_list([
            "owner__url", "owner__html_url", "repo__name", "repo__html_url",
        ]), *fields_filtered_results]

        print("Retrieving additional information of users...")
        processed_results = []
        # cache repeated user info to save request rate
        cached_user_info = self.cached_user_info
        # cache repo html url to ensure each result is unique after processing
        repo_set = set()
        # process result by adding user info
        for result in fields_filtered_results:
            if result["repo__html_url"] not in repo_set:
                res = cached_user_info.get(result["owner__url"], None)
                if not res:
                    res = requests.get(result["owner__url"], headers={
                        'user-agent': 'python',
                        'Authorization': "token {}".format(self.__token)
                    }).json()
                    cached_user_info[result["owner__url"]] = res
                processed_results.append({
                    **result,
                    "owner__email": res.get("email", None),
                    "owner__name": res.get("name", None),
                    "owner__username": res.get("login", None),
                    "owner__html_url": res.get("html_url", None)
                })
                repo_set.add(result["repo__html_url"])

        print("Processing results...")
        final_result_dict = {}
        for result in processed_results:
            if result["owner__username"] in final_result_dict:
                repos = final_result_dict[result["owner__username"]]["repos"]
                # if repo already exist
                if result["repo__name"] in repos:
                    # update history
                    repos[result["repo__name"]]["history"].append(
                        {
                            "date": repos[result["repo__name"]]["date"],
                            "status": repos[result["repo__name"]]["status"]
                        }
                    )
                    repos[result["repo__name"]]["status"] = "Redetected"
                    repos[result["repo__name"]]["date"] = str(datetime.datetime.now())
                else:
                    repos[result["repo__name"]] = {
                        "repo__name": result["repo__name"],
                        "repo__html_url": result["repo__html_url"],
                        "status": "New",
                        "date": str(datetime.datetime.now()),
                        "history": []
                    }
            elif self.previous_records and result["owner__username"] in self.previous_records:
                previous_record = self.previous_records[result["owner__username"]]
                repos = previous_record["repos"]
                # if repo already exist
                if result["repo__name"] in repos:
                    repos[result["repo__name"]]["history"].append(
                        {
                            "date": repos[result["repo__name"]]["date"],
                            "status": repos[result["repo__name"]]["status"]
                        }
                    )
                    repos[result["repo__name"]]["status"] = "Redetected"
                    repos[result["repo__name"]]["date"] = str(datetime.datetime.now())
                else:
                    repos[result["repo__name"]] = {
                        "repo__name": result["repo__name"],
                        "repo__html_url": result["repo__html_url"],
                        "status": "New",
                        "date": str(datetime.datetime.now()),
                        "history": []
                    }
                final_result_dict[result["owner__username"]] = previous_record
            else:
                final_result_dict[result["owner__username"]] = {
                    "owner__username": result["owner__username"],
                    "owner__name": result["owner__name"],
                    "owner__email": [result["owner__email"]],
                    "owner__html_url": result["owner__html_url"],
                    "repos": {
                        result["repo__name"]: {
                            "repo__name": result["repo__name"],
                            "repo__html_url": result["repo__html_url"],
                            "status": "New",
                            "date": str(datetime.datetime.now()),
                            "history": []
                        }
                    }
                }
        if chain:
            return final_result_dict

        final_result = {
            "results": []
        }
        for user in final_result_dict.values():
            repos = user.pop("repos")
            final_result["results"].append(
                {
                    **user,
                    "repos": [
                        {**repo_info} for repo_info in repos.values()
                    ]
                }
            )

        return final_result

    def execute_search_by_repo(self, ignore_warning: bool = False, chain: bool = False):
        """
        search by code
        :param ignore_warning:
        :return:
        """
        # pre-check
        if not self.__pre_check__(ignore_warning):
            return None

        # try to fire one request
        print("Start searching for repo...")
        first_result = self.client.search(self.search_query, "repo", )
        if not first_result:
            print("An error occurs, abort program", file=sys.stderr)
            return None
        else:
            print("Results retrieved from GitHub. Page: 1.")
        if first_result.total > 500 and not ignore_warning:
            confirm = None
            while not confirm:
                confirm = input("The number of search results is {}. It is so large that you may narrow search queries."
                                " The max retrievable number is 1000. Are you sure to proceed? [y/n]\n"
                                .format(first_result.total))
                if confirm.lower() not in ['y', 'n']:
                    confirm = None
                    print("Please enter 'y' or 'n': ")
                elif confirm.lower() == 'n':
                    return None

        fields_filtered_results = []
        code_search_result = first_result
        total = first_result.total
        page = 2  # page 1 has been requested
        while total > (page - 1) * 100 and page <= 10:
            fields_filtered_results = [*code_search_result.generate_list([
                "owner__url", "repo__name", "repo__html_url",
            ]), *fields_filtered_results]
            code_search_result = self.client.search(self.search_query, "repo", page=page)
            if not code_search_result:
                print("Error in search with GitHub rest APIs", file=sys.stderr)
                return None
            else:
                print("Results retrieved from GitHub. Page: {}.".format(page))
            page += 1
        fields_filtered_results = [*code_search_result.generate_list([
            "owner__url", "owner__html_url", "repo__name", "repo__html_url",
        ]), *fields_filtered_results]

        print("Retrieving additional information of users...")
        processed_results = []
        # cache repeated user info to save request rate
        # repo results are unique returned by GitHub
        cached_user_info = self.cached_user_info
        # cache repo html url to ensure each result is unique after processing
        for result in fields_filtered_results:
            res = cached_user_info.get(result["owner__url"], None)
            if not res:
                res = requests.get(result["owner__url"], headers={
                    'user-agent': 'python',
                    'Authorization': "token {}".format(self.__token)
                }).json()
                cached_user_info[result["owner__url"]] = res
            processed_results.append({
                **result,
                "owner__email": res.get("email", None),
                "owner__name": res.get("name", None),
                "owner__username": res.get("login", None),
                "owner__html_url": res.get("html_url", None)
            })

        print("Processing results...")
        final_result_dict = {}
        for result in processed_results:
            if result["owner__username"] in final_result_dict:
                repos = final_result_dict[result["owner__username"]]["repos"]
                # if repo already exist
                if result["repo__name"] in repos:
                    repos[result["repo__name"]]["history"].append(
                        {
                            "date": repos[result["repo__name"]]["date"],
                            "status": repos[result["repo__name"]]["status"]
                        }
                    )
                    repos[result["repo__name"]]["status"] = "Redetected"
                    repos[result["repo__name"]]["date"] = str(datetime.datetime.now())
                else:
                    repos[result["repo__name"]] = {
                        "repo__name": result["repo__name"],
                        "repo__html_url": result["repo__html_url"],
                        "status": "New",
                        "date": str(datetime.datetime.now()),
                        "history": []
                    }
            elif self.previous_records and result["owner__username"] in self.previous_records:
                previous_record = self.previous_records[result["owner__username"]]
                repos = previous_record["repos"]
                # if repo already exist
                if result["repo__name"] in repos:
                    repos[result["repo__name"]]["history"].append(
                        {
                            "date": repos[result["repo__name"]]["date"],
                            "status": repos[result["repo__name"]]["status"]
                        }
                    )
                    repos[result["repo__name"]]["status"] = "Redetected"
                    repos[result["repo__name"]]["date"] = str(datetime.datetime.now())
                else:
                    repos[result["repo__name"]] = {
                        "repo__name": result["repo__name"],
                        "repo__html_url": result["repo__html_url"],
                        "status": "New",
                        "date": str(datetime.datetime.now()),
                        "history": []
                    }
                final_result_dict[result["owner__username"]] = previous_record
            else:
                final_result_dict[result["owner__username"]] = {
                    "owner__username": result["owner__username"],
                    "owner__name": result["owner__name"],
                    "owner__email": [result["owner__email"]],
                    "owner__html_url": result["owner__html_url"],
                    "repos": {
                        result["repo__name"]: {
                            "repo__name": result["repo__name"],
                            "repo__html_url": result["repo__html_url"],
                            "status": "New",
                            "date": str(datetime.datetime.now()),
                            "history": []
                        }
                    }
                }

        if chain:
            return final_result_dict

        final_result = {
            "results": []
        }
        for user in final_result_dict.values():
            repos = user.pop("repos")
            final_result["results"].append(
                {
                    **user,
                    "repos": [
                        {**repo_info} for repo_info in repos.values()
                    ]
                }
            )

        return final_result

    def merge(self, results: list) -> dict:
        """
        merge intermediate results
        :param results:
        :return:
        """
        # merged results
        processed_results = []
        # map that used to <owner_username : index_in_processed_array>
        cache_user = {}
        # set that used to store visited repos
        cache_set = set()
        for result in results:
            for record in result.keys():
                curr = result[record]
                if record in cache_user:
                    processed_result = processed_results[cache_user[record]]
                    for repo_name in curr["repos"].keys():
                        if "{}/{}".format(record, repo_name) not in cache_set:
                            processed_result["repos"].append(
                                curr["repos"][repo_name]
                            )
                            cache_set.add("{}/{}".format(record, repo_name))
                else:
                    cache_user[record] = len(processed_results)
                    repos = curr.get("repos")
                    processed_results.append(
                        {
                            **curr,
                            "repos": [
                                {**repo_info} for repo_info in repos.values()
                            ]
                        }
                    )
                    for repo in repos.keys():
                        cache_set.add("{}/{}".format(record, repo))

        return {"results": processed_results}

    def execute(self, targets=None, ignore_warning: bool = False, chain: bool = False):
        """
        general execution function
        :param targets: "repo" or "code" or ["repo", "code"], by default "code"
        :param ignore_warning:
        :param chain:
        :return:
        """
        if not targets:
            return self.execute_search_by_code(ignore_warning=ignore_warning, chain=chain)
        elif isinstance(targets, list):
            results_of_different_targets = []
            for target in targets:
                if target == "repo":
                    res = self.execute_search_by_repo(ignore_warning=ignore_warning, chain=True)
                    if res:
                        results_of_different_targets.append(res)
                elif target == "code":
                    res = self.execute_search_by_code(ignore_warning=ignore_warning, chain=True)
                    if res:
                        results_of_different_targets.append(res)
            return self.merge(results_of_different_targets)
        else:
            if targets == "repo":
                return self.execute_search_by_repo(ignore_warning=ignore_warning, chain=False)
            elif targets == "code":
                return self.execute_search_by_code(ignore_warning=ignore_warning, chain=False)
            else:
                return None
