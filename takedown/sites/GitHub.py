"""
GitHub implement of BaseSite
---------------------------
GitHub search restful API docs: https://docs.github.com/en/free-pro-team@latest/rest/reference/search
"""
from .BaseSite import BaseSite
from requests import Session, Request
import sys


class GitHubClient(BaseSite):

    def __init__(self, **config):
        """
        init Github search
        :param config: a set of configs user would like to include, will provide more customization
        """
        super().__init__(**config)
        self.__dict__.update(config)
        self.base_url = 'https://api.github.com'
        self.__search_options = {
            'code': '/search/code',
            'commits': '/search/commits',
            'repositories': '/search/repositories'
        }
        self.__target_type = {
            'user': 'user:',
            'repo': 'repo:',
            'org': 'org:'
        }

    def authenticate(self, username, password, ):
        """
        OAuth will enable massive search
        :param username:
        :param password:
        :return:
        """
        pass

    def search(self, source: str, search_option: str, target: str = None, target_type: str = None, n_threads: int = None
               , **other_options):
        """
        main function for searching
        :param target_type:
        :param target:
        :param source:
        :param search_option:
        :param n_threads:
        :return:
        """
        # sanity checks
        if not search_option or search_option not in self.__search_options:
            print("Missing a search_option that falls in the category", file=sys.stderr)
            return None

        if not source or len(source.strip()) == 0:
            print("Missing a valid search input", file=sys.stderr)
            return None

        session = Session()
        # a very basic implementation of one API file content
        # TODO: error handling, enable more options, output classify
        if search_option == "code":
            print("Note that code search is unable to search the entire GitHub according to the provided "
                  "APIs. Consider using scrape() instead. Ignore this if you have a specific target to search.")
            if not target or not target_type or target_type not in self.__target_type:
                print("Missing a target or a target type for code searching", file=sys.stderr)
                session.close()
                return None
            params = {
                    'page': 1,
                    'per_page': 100,
                    'q': source + '+in:file+' + self.__target_type[target_type] + target
                }

        elif search_option == "repositories":
            params = {
                    'page': 1,
                    'per_page': 100,
                    'q': source
                }
            if target and target_type and target in target_type:
                params['q'] += '+' + self.__target_type[target_type] + target
            req = Request(
                method="get",
                url=self.base_url + self.__search_options[search_option],
                params="&".join("%s=%s" % (k, v) for k, v in params.items()),
                headers={
                    'accept': 'application/vnd.github.v3+json',
                    'user-agent': 'python'
                }
            ) \
                .prepare()
            res = session.send(req)
            if res.status_code == 200:
                print('Success')
            else:
                print(res.json(), file=sys.stderr)
        elif search_option == "commits":
            params = {
                    'page': 1,
                    'per_page': 100,
                    'q': source
                }
            if target and target_type and target in target_type:
                params['q'] += '+' + self.__target_type[target_type] + target
            req = Request(
                method="get",
                url=self.base_url + self.__search_options[search_option],
                params="&".join("%s=%s" % (k, v) for k, v in params.items()),
                headers={
                    'accept': 'application/vnd.github.cloak-preview',
                    'user-agent': 'python'
                }
            ) \
                .prepare()
            res = session.send(req)
            if res.status_code == 200:
                print('Success')
            else:
                print(res.json(), file=sys.stderr)
        else:
            print("search option error", file=sys.stderr)
        # clean up
        session.close()
