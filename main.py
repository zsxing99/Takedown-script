# main control file
# very simple script
from takedown.task.FindRepoTask import FindRepoTask
import sys


def main():
    options = sys.argv[1:]
    if len(options) < 2:
        print("Usage: python main.py your_search_pattern your_GitHub_token", file=sys.stderr)

    task = FindRepoTask()
    print(task.prepare(options[1], options[0]).execute_search_by_code())


if __name__ == '__main__':
    main()
