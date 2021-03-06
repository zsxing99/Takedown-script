"""
GitHub implement of BaseSite
---------------------------
GitHub search restful API docs: https://docs.github.com/en/free-pro-team@latest/rest/reference/search
"""
from .BaseSite import BaseSite, SiteResult
from requests import Session, Request
import typing
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
            'repo': '/search/repositories'
        }
        self.__target_type = {
            'user': 'user:',
            'repo': 'repo:',
            'org': 'org:'
        }
        self.__is_authenticated = False
        self.__OAuth_token = None

    def authenticate(self, token):
        """
        OAuth will enable massive search and search code without certain limits
        :return:
        """
        if self.__is_authenticated:
            print("Re-entered token")
        self.__is_authenticated = True
        self.__OAuth_token = token
        return self

    def search(self, source: str, search_option: str, target: str = None, target_type: str = None, n_threads: int = None
               , **other_options):
        """
        main function for searching
        :param target_type: 'user' | 'repo' | 'org'
        :param target: the target of target_type
        :param source: search string
        :param search_option: 'code' | 'commits'
        :param n_threads: not implemented
        :return: None | CodeSearchResult
        """
        # sanity checks
        if not search_option or search_option not in self.__search_options:
            print("Missing a search_option that falls in the category", file=sys.stderr)
            return None

        if not source or len(source.strip()) == 0:
            print("Missing a valid search controller", file=sys.stderr)
            return None

        session = Session()
        source = source.replace(" ", "+")
        results = None
        # a very basic implementation of one API file content
        if search_option == "code":
            params = {
                'page': other_options.get('page', 1),
                'per_page': 100,
                'q': source
            }
            headers = {
                'accept': 'application/vnd.github.v3+json',
                'user-agent': 'python'
            }
            if self.__is_authenticated:
                headers['Authorization'] = "token {}".format(self.__OAuth_token)
                if target and target_type and target in target_type:
                    params['q'] += '+' + self.__target_type[target_type] + target
            else:
                print("Note that code search is unable to search the entire GitHub according to the provided "
                      "APIs unless a token is provided through function authenticate()")
                if not target or not target_type or target_type not in self.__target_type:
                    print("Missing a target and a target type for code searching when no token is provided",
                          file=sys.stderr)
                    session.close()
                    return None
                params = {
                    'page': other_options.get('page', 1),
                    'per_page': 100,
                    'q': source + '+in:file+' + self.__target_type[target_type] + target
                }
            req = Request(
                method="get",
                url=self.base_url + self.__search_options[search_option],
                params="&".join("%s=%s" % (k, v) for k, v in params.items()),
                headers=headers
            ) \
                .prepare()
            res = session.send(req)
            if res.status_code == 200:
                results = CodeSearchResult(res.json())
            else:
                print(res.json(), file=sys.stderr)
        elif search_option == "commits":
            params = {
                'page': other_options.get('page', 1),
                'per_page': 100,
                'q': source
            }
            headers = {
                'accept': 'application/vnd.github.cloak-preview+json',
                'user-agent': 'python'
            }
            if self.__is_authenticated:
                headers['Authorization'] = "token {}".format(self.__OAuth_token)
            if target and target_type and target in target_type:
                params['q'] += '+' + self.__target_type[target_type] + target
            req = Request(
                method="get",
                url=self.base_url + self.__search_options[search_option],
                params="&".join("%s=%s" % (k, v) for k, v in params.items()),
                headers=headers
            ) \
                .prepare()
            res = session.send(req)
            if res.status_code == 200:
                results = CommitSearchResult(res.json())
            else:
                print(res.json(), file=sys.stderr)
        elif search_option == "repo":
            params = {
                'page': other_options.get('page', 1),
                'per_page': 100,
                'q': source
            }
            headers = {
                'accept': 'application/vnd.github.v3+json',
                'user-agent': 'python'
            }
            if self.__is_authenticated:
                headers['Authorization'] = "token {}".format(self.__OAuth_token)
                if target and target_type and target in target_type:
                    params['q'] += '+' + self.__target_type[target_type] + target
            else:
                print("Note that code search is unable to search the entire GitHub according to the provided "
                      "APIs unless a token is provided through function authenticate()")
                if not target or not target_type or target_type not in self.__target_type:
                    print("Missing a target and a target type for code searching when no token is provided",
                          file=sys.stderr)
                    session.close()
                    return None
                params = {
                    'page': other_options.get('page', 1),
                    'per_page': 100,
                    'q': source + '+in:file+' + self.__target_type[target_type] + target
                }
            req = Request(
                method="get",
                url=self.base_url + self.__search_options[search_option],
                params="&".join("%s=%s" % (k, v) for k, v in params.items()),
                headers=headers
            ) \
                .prepare()
            res = session.send(req)
            if res.status_code == 200:
                results = RepoSearchResult(res.json())
            else:
                print(res.json(), file=sys.stderr)
        else:
            print("search option error", file=sys.stderr)
        # clean up
        session.close()
        return results


class Item:
    def __init__(self):
        self.__fields = {}

    def store(self, key, value):
        self.__fields[key] = value

    def get(self, key):
        return self.__fields[key]

    def fields(self):
        return self.__fields.keys()


class CodeSearchResult(SiteResult):

    def __init__(self, json, **config):
        super().__init__(**config)
        self.__raw_results = json
        self.__items = self.__process()
        self.total = json["total_count"]
        self.completed = json["incomplete_results"]

    def __process(self):
        items = []
        raw_items = self.__raw_results["items"]
        for raw_item in raw_items:
            item = Item()
            repo = raw_item.pop("repository")
            owner = repo.pop("owner")
            for k, v in raw_item.items():
                item.store('file__' + k, v)
            for k, v in repo.items():
                item.store('repo__' + k, v)
            for k, v in owner.items():
                item.store('owner__' + k, v)
            items.append(item)
        return items

    def print_list(self, fields: typing.Union[str, typing.Iterable] = "owner__login", **config):
        """
        generate the list of output returned by GitHub
        :param fields: list | string, see get_fields()
        :param config:
        :return:
        """
        if isinstance(fields, str):
            print("".join(map(lambda i: "{}\n".format(i.get(fields)), self.__items)))
        else:
            for item in self.__items:
                print(" ".join([item.get(field) for field in fields]))

    def generate_list(self, fields: typing.Union[str, typing.Iterable] = "owner__login", **config) -> list:
        res = []
        if isinstance(fields, str):
            res = map(lambda i: i.get(fields), self.__items)
        else:
            for item in self.__items:
                res.append({
                    field: item.get(field) for field in fields
                })
        return res

    def get_fields(self) -> set:
        """
        get all available fields that can be accessed
        :return:
        """

        return set() if len(self.__items) == 0 else self.__items[0].fields()


class CommitSearchResult(SiteResult):

    def __init__(self, json, **config):
        super().__init__(**config)
        self.__raw_results = json
        self.__items = self.__process()
        self.total = json["total_count"]
        self.completed = json["incomplete_results"]

    def __process(self):
        items = []
        raw_items = self.__raw_results["items"]
        for raw_item in raw_items:
            item = Item()
            author = raw_item.pop("author")
            committer = raw_item.pop("committer")
            repo = raw_item.pop("repository")
            for k, v in raw_item.items():
                item.store('commit__' + k, v)
            for k, v in repo.items():
                item.store('repo__' + k, v)
            for k, v in author.items():
                item.store('author__' + k, v)
            for k, v in committer.items():
                item.store('committer__' + k, v)
            items.append(item)
        return items

    def print_list(self, fields: typing.Union[str, typing.Iterable] = "owner__login", **config) -> None:
        """
        generate the list of output returned by GitHub
        :param fields: list | string, see get_fields()
        :param config:
        :return:
        """
        if isinstance(fields, str):
            print("".join(map(lambda i: "{}\n".format(i.get(fields)), self.__items)))
        else:
            for item in self.__items:
                print(" ".join([item.get(field) for field in fields]))

    def generate_list(self, fields: typing.Union[str, typing.Iterable] = "owner__login", **config) -> []:
        res = []
        if isinstance(fields, str):
            res = map(lambda i: i.get(fields), self.__items)
        else:
            for item in self.__items:
                res.append({
                    field: item.get(field) for field in fields
                })
        return res

    def get_fields(self) -> set:
        """
        get all available fields that can be accessed
        :return:
        """

        return set() if len(self.__items) == 0 else self.__items[0].fields()


class RepoSearchResult(SiteResult):

    def __init__(self, json, **config):
        super().__init__(**config)
        self.__raw_results = json
        self.__items = self.__process()
        self.total = json["total_count"]
        self.completed = json["incomplete_results"]

    def __process(self):
        items = []
        raw_items = self.__raw_results["items"]
        for raw_item in raw_items:
            item = Item()
            owner = raw_item.pop("owner")
            for k, v in raw_item.items():
                item.store('repo__' + k, v)
            for k, v in owner.items():
                item.store('owner__' + k, v)
            items.append(item)
        return items

    def print_list(self, fields: typing.Union[str, typing.Iterable] = "owner__login", **config) -> None:
        """
        generate the list of output returned by GitHub
        :param fields: list | string, see get_fields()
        :param config:
        :return:
        """
        if isinstance(fields, str):
            print("".join(map(lambda i: "{}\n".format(i.get(fields)), self.__items)))
        else:
            for item in self.__items:
                print(" ".join([item.get(field) for field in fields]))

    def generate_list(self, fields: typing.Union[str, typing.Iterable] = "owner__login", **config) -> []:
        res = []
        if isinstance(fields, str):
            res = map(lambda i: i.get(fields), self.__items)
        else:
            for item in self.__items:
                res.append({
                    field: item.get(field) for field in fields
                })
        return res

    def get_fields(self) -> set:
        """
        get all available fields that can be accessed
        :return:
        """

        return set() if len(self.__items) == 0 else self.__items[0].fields()
