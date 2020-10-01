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
        self.search_options = {
            'code': '/search/code',
            'commits': '/search/commits',
            'issues': '/search/issues',
            'repositories': '/search/repositories'
        }

    def authenticate(self, username, password, ):
        """
        OAuth will enable massive search
        :param username:
        :param password:
        :return:
        """
        pass

    def search(self, source: str, search_option: str, n_threads=None):
        """
        main function for searching
        :param source:
        :param search_option:
        :param n_threads:
        :return:
        """
        # sanity checks
        if not search_option or search_option not in self.search_options:
            print("Enter a search_option falls in a category", file=sys.stderr)
            return None

        if not source or len(source.strip()) == 0:
            print("Enter a valid search input", file=sys.stderr)
            return None

        session = Session()
        # a very basic implementation of one API file content that search in my own repo
        # TODO: error handling, enable more options, output classify
        if search_option == "code":
            params = {
                    'page': 1,
                    'per_page': 100,
                    'q': source + '+in:file' + '+user:zsxing99'
                }
            req = Request(
                method="get",
                url=self.base_url + self.search_options[search_option],
                params="&".join("%s=%s" % (k,v) for k,v in params.items()),
                headers={
                    'accept': 'application/vnd.github.v3+json',
                    'user-agent': 'python'
                }
            ) \
                .prepare()
            res = session.send(req)
            if res.status_code == 200:
                print(res.json())
            else:
                print(res.json())

        # clean up
        session.close()
