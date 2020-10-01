# main control file
from takedown.sites.GitHub import GitHubClient


def main():
    # test only
    g = GitHubClient()
    t = g.authenticate("").search("react", "code", )
    t.generate_list()

if __name__ == '__main__':
    main()
