# very simple script
from takedown.client.GitHub import GitHubClient
import sys


def main():
    options = sys.argv[1:]
    if len(options) < 2:
        print("Usage: python client_example.py your_search_pattern your_GitHub_token", file=sys.stderr)

    client = GitHubClient()
    # authenticate and search
    # you can choose not to authenticate, but limitations apply. check docs for details
    results = client.authenticate("Your personal GitHub token").search("this is awesome", "code", )
    # check fields options that can be used for list generation
    print(results.get_fields())
    results.generate_list(['owner__login', 'owner__html_url'])


if __name__ == '__main__':
    main()
