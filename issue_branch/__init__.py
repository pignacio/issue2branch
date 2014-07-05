from .config import get_config
from .trackers import get_issue_tracker


def main():
    config = get_config()
    get_issue_tracker(config).run()


if __name__ == "__main__":
    main()
