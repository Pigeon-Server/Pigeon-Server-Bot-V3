import sys
from datetime import datetime
from unittest import TestLoader, TextTestRunner


def get_suite():
    return TestLoader().discover(__name__, "test*.py")


def main() -> None:
    with open(f"./report/report_{datetime.strftime(datetime.now(), '%Y-%m-%d_%H_%M_%S')}.txt", "w") as f:
        runner = TextTestRunner(stream=f, descriptions=True, verbosity=2)
        suite = get_suite()
        runner.run(suite)


if __name__ == '__main__':
    main()
