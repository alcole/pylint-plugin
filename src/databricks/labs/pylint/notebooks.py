import astroid
from pylint.checkers import BaseRawFileChecker


class NotebookChecker(BaseRawFileChecker):
    __implements__ = (BaseRawFileChecker,)

    name = "databricks-notebooks"
    msgs = {
        "E9996": (
            "Notebooks should not have more than 75 cells",
            "notebooks-too-many-cells",
            "Used when the number of cells in a notebook is greater than 75",
        ),
        "E9994": (
            "Using %run is not allowed",
            "notebooks-percent-run",
            "Used when `# MAGIC %run` comment is used",
        ),
    }

    options = (
        (
            "max-cells",
            {
                "default": 75,
                "type": "int",
                "metavar": "<int>",
                "help": "Maximum number of cells in the notebook",
            },
        ),
    )

    def process_module(self, node: astroid.Module):
        """Read raw module. Need to do some tricks, as `ast` doesn't provide access for comments.

        Alternative libraries that can parse comments along with the code:
        - https://github.com/Instagram/LibCST/ (MIT + PSF)
        - https://github.com/python/cpython/tree/3.10/Lib/lib2to3 (PSF), removed in Python 3.12
        - https://github.com/t3rn0/ast-comments (MIT)
        - https://github.com/facebookincubator/bowler (MIT), abandoned
        - https://github.com/PyCQA/redbaron (LGPLv3)
        """
        cells = 1
        with node.stream() as stream:
            for lineno, line in enumerate(stream):
                lineno += 1
                if lineno == 1 and line != b"# Databricks notebook source\n":
                    # this is not a Databricks notebook
                    return
                if line == b"# COMMAND ----------\n":
                    cells += 1
                if cells > self.linter.config.max_cells:
                    self.add_message("notebooks-too-many-cells", line=lineno)
                    continue
                if line.startswith(b"# MAGIC %run"):
                    self.add_message("notebooks-percent-run", line=lineno)


def register(linter):
    linter.register_checker(NotebookChecker(linter))
