# main control file
from takedown.sites.GitHub import GitHubClient


def main():
    # test only
    g = GitHubClient()
    g.search("react", "commits", )


if __name__ == '__main__':
    main()
