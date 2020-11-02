"""
FindRepoTask
--------------------------------------------------
Run tool to find repos that should be taken down
    1. Tool should group repos by owner, if one owner has multiple repos in violation
    2. Newly found repos are tagged as “new”
--------------------------------------------------
execution result will be an array of dict
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
        self.file_type = 'csv'
        self.previous_records = None
        # save rate limit and bandwidth with GitHub requests, cache user_info
        self.cached_user_info = {}

    def prepare(self, token: str, search_query: str, file_type: str = None, previous_records: dict = None):
        """
        prepare the task
        :param token: input github token
        :param search_query: input search_query
        :param file_type: the format of output file wanted
        :param previous_records: previous records of searched repos
        :return: self instance
        """
        self.client.authenticate(token)
        self.__token = token
        self.__is_authenticated = True
        self.search_query = search_query
        if file_type:
            self.file_type = file_type
        if previous_records:
            # cache username and corresponding repo
            users_list = previous_records["results"]
            previous_records_cache = {}
            for user in users_list:
                repos = user.pop("repos")
                user["repos"] = {
                    repo["repo__name"]: repo for repo in repos
                }
                previous_records_cache[user["owner__username"]] = user
            self.previous_records = previous_records_cache
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
        :param ignore_warning:
        :return:
        """
        # pre-check
        if not self.__pre_check__(ignore_warning):
            return None

        # try to fire one request
        first_result = self.client.search(self.search_query, "code", )
        if not first_result:
            print("An error occurs, abort program", file=sys.stderr)
            return None
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
            page += 1
        fields_filtered_results = [*code_search_result.generate_list([
            "owner__url", "owner__html_url", "repo__name", "repo__html_url",
        ]), *fields_filtered_results]

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
                    "owner__html_url": res.get("owner__html_url", None)
                })
                repo_set.add(result["repo__html_url"])

        final_result_dict = {}
        for result in processed_results:
            if result["owner__username"] in final_result_dict:
                repos = final_result_dict[result["owner__username"]]["repos"]
                # if repo already exist
                if result["repo__name"] in repos:
                    repos[result["repo__name"]]["status"] = "Re-detected"
                    repos[result["repo__name"]]["latest_detected_date"] = datetime.datetime.now()
                else:
                    repos[result["repo__name"]] = {
                        "repo__name": result["repo__name"],
                        "repo__html_url": result["repo__html_url"],
                        "status": "New",
                        "latest_detected_date": datetime.datetime.now()
                    }
            elif self.previous_records and result["owner__username"] in self.previous_records:
                previous_record = self.previous_records[result["owner__username"]]
                repos = previous_record["repos"]
                # if repo already exist
                if result["repo__name"] in repos:
                    repos[result["repo__name"]]["status"] = "Re-detected"
                    repos[result["repo__name"]]["latest_detected_date"] = datetime.datetime.now()
                else:
                    repos[result["repo__name"]] = {
                        "repo__name": result["repo__name"],
                        "repo__html_url": result["repo__html_url"],
                        "status": "New",
                        "latest_detected_date": datetime.datetime.now()
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
                            "latest_detected_date": datetime.datetime.now()
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
        first_result = self.client.search(self.search_query, "repo", )
        if not first_result:
            print("An error occurs, abort program", file=sys.stderr)
            return None
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
            page += 1
        fields_filtered_results = [*code_search_result.generate_list([
            "owner__url", "owner__html_url", "repo__name", "repo__html_url",
        ]), *fields_filtered_results]

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
            processed_results.append({
                **result,
                "owner__email": res.get("email", None),
                "owner__name": res.get("name", None),
                "owner__username": res.get("login", None),
                "owner__html_url": res.get("owner__html_url", None)
            })

        final_result_dict = {}
        for result in processed_results:
            if result["owner__username"] in final_result_dict:
                repos = final_result_dict[result["owner__username"]]["repos"]
                # if repo already exist
                if result["repo__name"] in repos:
                    repos[result["repo__name"]]["status"] = "Re-detected"
                    repos[result["repo__name"]]["latest_detected_date"] = datetime.datetime.now()
                else:
                    repos[result["repo__name"]] = {
                        "repo__name": result["repo__name"],
                        "repo__html_url": result["repo__html_url"],
                        "status": "New",
                        "latest_detected_date": datetime.datetime.now()
                    }
            elif self.previous_records and result["owner__username"] in self.previous_records:
                previous_record = self.previous_records[result["owner__username"]]
                repos = previous_record["repos"]
                # if repo already exist
                if result["repo__name"] in repos:
                    repos[result["repo__name"]]["status"] = "Re-detected"
                    repos[result["repo__name"]]["latest_detected_date"] = datetime.datetime.now()
                else:
                    repos[result["repo__name"]] = {
                        "repo__name": result["repo__name"],
                        "repo__html_url": result["repo__html_url"],
                        "status": "New",
                        "latest_detected_date": datetime.datetime.now()
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
                            "latest_detected_date": datetime.datetime.now()
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

