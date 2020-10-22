## TakeDown Script
A simple python script/package that allows users to search potential
copyright violated information on GitHub(probably more sites in future).
It returns the targets with a set of usernames.

### Requirements
```
python >= 3.8
requests~=2.23.0
pandas~=1.0.3
```

A `requirements.txt` is provided, so simply run:
```
pip install -r requirements.txt
```
So all dependencies will be added. Of course you should have `pip` installed.

### Usage
There are a simple starter script provided called `main.py` and the entire package called `takedown`.

#### script
On command line, run:
```
python main.py your_search_pattern your_GitHub_personal_token
```
As noted, the script is very simple. It is only a starter script. You can customize your own by using
the `takedown` package.

There aren't too much options the script provides for now, but might be extended.

#### package
There are only GitHub TakeDown implemented now, so here's a piece of sample for you.

```python
from takedown.client.GitHub import GitHubClient

client = GitHubClient()
# authenticate and search
# you can choose not to authenticate, but limitations apply. check docs for details
results = client.authenticate("Your personal GitHub token").search("this is awesome", "code", )
# check fields options that can be used for list generation
print(results.get_fields())
results.generate_list(['owner__login', 'owner__html_url'])
```

### Notes
For GitHub client to search, there are certain restrictions:
1. You must provided a personal token to search the entire GitHuh site, or
you must specify a user, org, or repo.
2. The max length limit of search query is 256, so keep it shorter.
3. There is a rate limit of sending GitHub REST requests.

Consult this [page](https://docs.github.com/en/free-pro-team@latest/rest/reference/search) if you have more questions.

To get a personal token(free), check 
this [tutorial](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token).

The implementation only returns the list of max 100 search results. It is very uncommon 
that will be more than 50 repos or codes results that 
match a very specific pattern. Your search is either too broad(so narrow the search down), or your
work is entirely leaked. Limits might be raised in the future.
