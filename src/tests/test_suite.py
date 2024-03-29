from datetime import datetime
from unittest import TestLoader

from HTMLTestRunner.HTMLTestRunner import HTMLTestRunner


def get_suite():
    return TestLoader().discover(__name__, "test*.py")


def main() -> None:
    with open(f"./report/report_{datetime.strftime(datetime.now(), '%Y-%m-%d_%H_%M_%S')}.html", "w") as f:
        runner = HTMLTestRunner(stream=f, title="Test Report", verbosity=2)
        suite = get_suite()
        runner.run(suite)


if __name__ == '__main__':
    main()
