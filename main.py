# main control file
# very simple script
from takedown.client.GitHub import GitHubClient
import sys


def main():
    options = sys.argv[1:]
    if len(options) < 2:
        print("Usage: python main.py your_search_pattern your_GitHub_token", file=sys.stderr)

    client = GitHubClient()
    results = client.authenticate(options[1]).search(options[0], "code", )
    if not results:
        return
    results.generate_list()


if __name__ == '__main__':
    main()
