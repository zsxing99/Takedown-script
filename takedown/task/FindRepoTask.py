"""
FindRepoTask
--------------------------------------------------
Run tool to find repos that should be taken down
    1. Tool should group repos by owner, if one owner has multiple repos in violation
    2. Newly found repos are tagged as “new”
"""

from .BaseTask import BaseTask
from takedown.client.GitHub import GitHubClient
import pandas as pd
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

    def prepare(self, token: str, search_query: str, file_type: str = None, previous_records: pd.DataFrame = None):
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

    def execute_search_by_code(self, ignore_warning: bool = False):
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
            page += 1
        fields_filtered_results = [*code_search_result.generate_list([
            "owner__url", "owner__html_url", "repo__name", "repo__html_url",
        ]), *fields_filtered_results]

        processed_results = []
        # process result
        for result in fields_filtered_results:
            res = requests.get(result["owner__url"], headers={
                'user-agent': 'python',
                'Authorization': "token {}".format(self.__token)
            }).json()
            processed_results.append({
                **result,
                "owner__email": res.get("email", None),
                "owner__name": res.get("name", None),
                "owner__username": res.get("login", None)
            })

        # if provided with an older pd.Dataframe
        previous_records_map = None  # store the mapping info as username to a set of repo names
        if self.previous_records:
            previous_records_map = {}
            for index, row in self.previous_records.iterrows():
                if row["owner__username"] in previous_records_map:
                    previous_records_map[row["owner__username"]].add(row["repo__name"])
                else:
                    previous_records_map[row["owner__username"]] = {row["repo__name"]}

        columns = ["owner__username", "owner__name", "owner__email", "owner__html_url", "repo__name", "repo__html_url",
                   "status", "latest_detected_date"]
        results_df = pd.DataFrame(columns=columns)
        repo_set = set()
        for result in processed_results:
            if result["repo__html_url"] in repo_set:
                continue
            else:
                repo_set.add(result["repo__html_url"])
            status = "New"
            if previous_records_map:
                if result["owner__username"] in previous_records_map and result["repo__name"] in \
                        previous_records_map[result["owner__username"]]:
                    status = "Re-detected"
            result["status"] = status
            result["latest_detected_date"] = datetime.datetime.now()
            results_df.loc[len(results_df)] = [result[key] for key in columns]

        return results_df

    def execute_search_by_repo(self, ignore_warning: bool = False):
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
            page += 1
        fields_filtered_results = [*code_search_result.generate_list([
            "owner__url", "owner__html_url", "repo__name", "repo__html_url",
        ]), *fields_filtered_results]

        processed_results = []
        # process result
        for result in fields_filtered_results:
            res = requests.get(result["owner__url"], headers={
                'user-agent': 'python',
                'Authorization': "token {}".format(self.__token)
            }).json()
            processed_results.append({
                **result,
                "owner__email": res.get("email", None),
                "owner__name": res.get("name", None),
                "owner__username": res.get("login", None)
            })

        # if provided with an older pd.Dataframe
        previous_records_map = None  # store the mapping info as username to a set of repo names
        if self.previous_records:
            previous_records_map = {}
            for index, row in self.previous_records.iterrows():
                if row["owner__username"] in previous_records_map:
                    previous_records_map[row["owner__username"]].add(row["repo__name"])
                else:
                    previous_records_map[row["owner__username"]] = {row["repo__name"]}

        columns = ["owner__username", "owner__name", "owner__email", "owner__html_url", "repo__name", "repo__html_url",
                   "status", "latest_detected_date"]
        results_df = pd.DataFrame(columns=columns)
        repo_set = set()
        for result in processed_results:
            if result["repo__html_url"] in repo_set:
                continue
            else:
                repo_set.add(result["repo__html_url"])
            status = "New"
            if previous_records_map:
                if result["owner__username"] in previous_records_map and result["repo__name"] in \
                        previous_records_map[result["owner__username"]]:
                    status = "Re-detected"
            result["status"] = status
            result["latest_detected_date"] = datetime.datetime.now()
            results_df.loc[len(results_df)] = [result[key] for key in columns]

        return results_df