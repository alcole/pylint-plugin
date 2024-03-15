from databricks.labs.pylint.dbutils import DbutilsChecker
from databricks.labs.pylint.legacy import LegacyChecker
from databricks.labs.pylint.notebooks import NotebookChecker


def register(linter):
    linter.register_checker(NotebookChecker(linter))
    linter.register_checker(DbutilsChecker(linter))
    linter.register_checker(LegacyChecker(linter))