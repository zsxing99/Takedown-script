# main control file
from takedown.sites.GitHub import GitHubClient


def main():
    # test only
    g = GitHubClient()
    g.authenticate("").search("react", "code", )


if __name__ == '__main__':
    main()
