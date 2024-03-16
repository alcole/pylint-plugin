<!-- FOR CONTRIBUTORS: Edit this file in Visual Studio Code with the recommended extensions, so that we update the table of contents automatically -->
# PyLint Plugin for Databricks


[![python](https://img.shields.io/badge/python-3.8,%203.9,%20,3.10,%203.11,%203.12-green)](https://github.com/databrickslabs/pylint-plugin/actions/workflows/push.yml)
[![codecov](https://codecov.io/github/databrickslabs/pylint-plugin/graph/badge.svg?token=x1JSVddfZa)](https://codecov.io/github/databrickslabs/pylint-plugin) [![lines of code](https://tokei.rs/b1/github/databrickslabs/pylint-plugin)]([https://codecov.io/github/databrickslabs/pylint-plugin](https://github.com/databrickslabs/pylint-plugin))

[PyLint](https://www.pylint.org/) serves as a valuable tool for developers by performing various checks on code quality.
It scrutinizes the length of lines, ensures conformity to coding standards regarding variable naming, validates 
the usage of imported modules, verifies the implementation of declared interfaces, identifies instances of duplicated 
code, and [much more](https://pylint.readthedocs.io/en/latest/user_guide/checkers/features.html). This plugin extends 
PyLint with checks for common mistakes and issues in Python code specifically in Databricks Environment.

<!-- TOC -->
* [PyLint Plugin for Databricks](#pylint-plugin-for-databricks)
* [Installation as PyLint plugin](#installation-as-pylint-plugin)
* [Integration with Databricks CLI](#integration-with-databricks-cli)
* [PyLint Ecosystem](#pylint-ecosystem)
* [Why not (just) Ruff?](#why-not-just-ruff)
* [Automated code analysis](#automated-code-analysis)
  * [`databricks-airflow` checker](#databricks-airflow-checker)
    * [`W8901`: `missing-data-security-mode`](#w8901-missing-data-security-mode)
    * [`W8902`: `unsupported-runtime`](#w8902-unsupported-runtime)
  * [`databricks-dbutils` checker](#databricks-dbutils-checker)
    * [`R8903`: `dbutils-fs-cp`](#r8903-dbutils-fs-cp)
    * [`R8904`: `dbutils-fs-head`](#r8904-dbutils-fs-head)
    * [`R8905`: `dbutils-fs-ls`](#r8905-dbutils-fs-ls)
    * [`R8906`: `dbutils-fs-mount`](#r8906-dbutils-fs-mount)
    * [`R8907`: `dbutils-credentials`](#r8907-dbutils-credentials)
    * [`R8908`: `dbutils-notebook-run`](#r8908-dbutils-notebook-run)
    * [`R8909`: `pat-token-leaked`](#r8909-pat-token-leaked)
    * [`R8910`: `internal-api`](#r8910-internal-api)
  * [`databricks-legacy` checker](#databricks-legacy-checker)
    * [`R8911`: `legacy-cli`](#r8911-legacy-cli)
    * [`W8912`: `incompatible-with-uc`](#w8912-incompatible-with-uc)
  * [`databricks-notebooks` checker](#databricks-notebooks-checker)
    * [`C8913`: `notebooks-too-many-cells`](#c8913-notebooks-too-many-cells)
    * [`R8914`: `notebooks-percent-run`](#r8914-notebooks-percent-run)
  * [`spark` checker](#spark-checker)
    * [`C8915`: `spark-outside-function`](#c8915-spark-outside-function)
    * [`C8917`: `use-display-instead-of-show`](#c8917-use-display-instead-of-show)
    * [`W8916`: `no-spark-argument-in-function`](#w8916-no-spark-argument-in-function)
  * [Testing in isolation](#testing-in-isolation)
* [Project Support](#project-support)
<!-- TOC -->

# Installation as PyLint plugin

You can install this project via `pip`:

```bash
pip install databricks-labs-pylint-plugin
```

and then use it with `pylint`:

```bash
pylint --load-plugins=databricks.labs.pylint.all <your-python-file>.py
```

[[back to top](#databricks-labs-pylint-plugin)]

# Integration with Databricks CLI

You can use this plugin with Databricks CLI to check individual notebooks or entire directories. 

First, you need to install this plugin locally:

```bash
databricks labs install pylint-plugin
```

Then, you can call the `nbcheck` command without any arguments to lint all Python notebooks in you home folder:

```bash
databricks labs pylint-plugin nbcheck
```

Or you can specify a `--path` flag to lint a specific notebook or folder:

```bash
databricks labs pylint-plugin nbcheck --path /Users/me@example.com/PrepareData
```

[[back to top](#databricks-labs-pylint-plugin)]

# PyLint Ecosystem

More than [400k repositories](https://github.com/pylint-dev/pylint/network/dependents?dependent_type=PACKAGE) use PyLint,
and it is one of the most popular static code analysis tools in the Python ecosystem. This plugin allows you to work with
PyLint in the same way you are used to, but with additional checks for Databricks-specific issues. It is also compatible
with the following PyLint integrations:
- [VSCode PyLint extension](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint) (MIT License)
- [IntelliJ/PyCharm PyLint plugin](https://plugins.jetbrains.com/plugin/11084-pylint) (Apache License 2.0)
- [Airflow Plugin](https://github.com/BasPH/pylint-airflow) (MIT License)
- [GitHub Action](https://github.com/marketplace/actions/pylint-with-dynamic-badge) (MIT License)
- [Azure DevOps Task](https://marketplace.visualstudio.com/items?itemName=dazfuller.pylint-task) (MIT License)
- [GitLab CodeClimate](https://pypi.org/project/pylint-gitlab/) (GPLv3 License)

[[back to top](#databricks-labs-pylint-plugin)]

# Why not (just) Ruff?

Even though [Ruff](https://docs.astral.sh/ruff/) is [10x+ faster](https://pythonspeed.com/articles/pylint-flake8-ruff/) 
than PyLint, it doesn't have a [plugin system yet](https://github.com/astral-sh/ruff/issues/283), nor does it have 
a [feature parity with PyLint](https://github.com/astral-sh/ruff/issues/970) yet. Other 
[projects](https://github.com/databrickslabs/ucx) use [MyPy](https://mypy.readthedocs.io/), 
[Ruff](https://docs.astral.sh/ruff/), and [PyLint](https://www.pylint.org/) together to achieve
the most comprehensive code analysis. You can try using Ruff and [just the checkers from this plugin](#testing-in-isolation) 
in the same CI pipeline and pre-commit hook.

[[back to top](#databricks-labs-pylint-plugin)]

# Automated code analysis

Every check has a code, that follows an [existing convention](https://github.com/pylint-dev/pylint/blob/v3.1.0/pylint/checkers/__init__.py#L5-L41):
 - `{I,C,R,W,E,F}89{0-9}{0-9}`, where `89` is the base ID for this plugin.
 - `{I,C,R,W,E,F}` mean for `Info`, `Convention`, `Refactor`, `Warning`, `Error`, and `Fatal`.

[[back to top](#databricks-labs-pylint-plugin)]

<!-- CHECKS -->

## `databricks-airflow` checker

[[back to top](#databricks-labs-pylint-plugin)]

### `W8901`: `missing-data-security-mode`

XXX cluster missing `data_security_mode` required for Unity Catalog compatibility. Before you enable Unity Catalog, you must set the `data_security_mode` to 'NONE', so that your existing jobs would keep the same behavior. Failure to do so may cause your jobs to fail with unexpected errors.

[[back to top](#databricks-labs-pylint-plugin)]

### `W8902`: `unsupported-runtime`

XXX cluster has unsupported runtime: XXX. The runtime version is not supported by Unity Catalog. Please upgrade to a runtime greater than or equal to 11.3.

[[back to top](#databricks-labs-pylint-plugin)]

## `databricks-dbutils` checker

[[back to top](#databricks-labs-pylint-plugin)]

### `R8903`: `dbutils-fs-cp`

Use Databricks SDK instead: w.dbfs.copy(XXX, XXX). Migrate all usage of dbutils to Databricks SDK. See the more detailed documentation at https://databricks-sdk-py.readthedocs.io/en/latest/workspace/files/dbfs.html

[[back to top](#databricks-labs-pylint-plugin)]

### `R8904`: `dbutils-fs-head`

Use Databricks SDK instead: with w.dbfs.download(XXX) as f: f.read(). Migrate all usage of dbutils to Databricks SDK. See the more detailed documentation at https://databricks-sdk-py.readthedocs.io/en/latest/workspace/files/dbfs.html

[[back to top](#databricks-labs-pylint-plugin)]

### `R8905`: `dbutils-fs-ls`

Use Databricks SDK instead: w.dbfs.list(XXX). Migrate all usage of dbutils to Databricks SDK. See the more detailed documentation at https://databricks-sdk-py.readthedocs.io/en/latest/workspace/files/dbfs.html

[[back to top](#databricks-labs-pylint-plugin)]

### `R8906`: `dbutils-fs-mount`

Mounts are not supported with Unity Catalog, switch to using Unity Catalog Volumes instead. Migrate all usage to Unity Catalog

[[back to top](#databricks-labs-pylint-plugin)]

### `R8907`: `dbutils-credentials`

Credentials utility is not supported with Unity Catalog. Migrate all usage to Unity Catalog

[[back to top](#databricks-labs-pylint-plugin)]

### `R8908`: `dbutils-notebook-run`

Use Databricks SDK instead: w.jobs.submit(
                tasks=[jobs.SubmitTask(existing_cluster_id=...,
                                       notebook_task=jobs.NotebookTask(notebook_path=XXX),
                                       task_key=...)
                ]).result(timeout=timedelta(minutes=XXX)). Migrate all usage of dbutils to Databricks SDK. See the more detailed documentation at https://databricks-sdk-py.readthedocs.io/en/latest/workspace/jobs/jobs.html

[[back to top](#databricks-labs-pylint-plugin)]

### `R8909`: `pat-token-leaked`

Use Databricks SDK instead: from databricks.sdk import WorkspaceClient(); w = WorkspaceClient(). Do not hardcode secrets in code, use Databricks SDK instead, which natively authenticates in Databricks Notebooks. See more at https://databricks-sdk-py.readthedocs.io/en/latest/authentication.html

[[back to top](#databricks-labs-pylint-plugin)]

### `R8910`: `internal-api`

Do not use internal APIs, rewrite using Databricks SDK: XXX. Do not use internal APIs. Use Databricks SDK for Python: https://databricks-sdk-py.readthedocs.io/en/latest/index.html

[[back to top](#databricks-labs-pylint-plugin)]

## `databricks-legacy` checker

[[back to top](#databricks-labs-pylint-plugin)]

### `R8911`: `legacy-cli`

Don't use databricks_cli, use databricks.sdk instead: pip install databricks-sdk. Migrate all usage of Legacy CLI to Databricks SDK. See the more detailed documentation at https://databricks-sdk-py.readthedocs.io/en/latest/index.html

[[back to top](#databricks-labs-pylint-plugin)]

### `W8912`: `incompatible-with-uc`

Incompatible with Unity Catalog: XXX. Migrate all usage to Databricks Unity Catalog. Use https://github.com/databrickslabs/ucx for more details

[[back to top](#databricks-labs-pylint-plugin)]

## `databricks-notebooks` checker

[[back to top](#databricks-labs-pylint-plugin)]

### `C8913`: `notebooks-too-many-cells`

Notebooks should not have more than 75 cells. Otherwise, it's hard to maintain and understand the notebook for other people and the future you

[[back to top](#databricks-labs-pylint-plugin)]

### `R8914`: `notebooks-percent-run`

Using %run is not allowed. Use functions instead of %run to avoid side effects and make the code more testable. If you need to share code between notebooks, consider creating a library. If still need to call another code as a separate job, use Databricks SDK for Python: https://databricks-sdk-py.readthedocs.io/en/latest/index.html

[[back to top](#databricks-labs-pylint-plugin)]

## `spark` checker

[[back to top](#databricks-labs-pylint-plugin)]

### `C8915`: `spark-outside-function`

Using spark outside the function is leading to untestable code. Do not use global spark object, pass it as an argument to the function instead, so that the function becomes testable in a CI/CD pipelines.

[[back to top](#databricks-labs-pylint-plugin)]

### `C8917`: `use-display-instead-of-show`

Rewrite to display in a notebook: display(XXX). Use display() instead of show() to visualize the data in a notebook.

[[back to top](#databricks-labs-pylint-plugin)]

### `W8916`: `no-spark-argument-in-function`

Function XXX is missing a 'spark' argument. Function refers to a global spark variable, which may not always be available. Pass the spark object as an argument to the function instead, so that the function becomes testable in a CI/CD pipelines.

[[back to top](#databricks-labs-pylint-plugin)]

## Testing in isolation
To test this plugin in isolation, you can use the following command:

```bash
pylint --load-plugins=databricks.labs.pylint.all --disable=all --enable=missing-data-security-mode,unsupported-runtime,dbutils-fs-cp,dbutils-fs-head,dbutils-fs-ls,dbutils-fs-mount,dbutils-credentials,dbutils-notebook-run,pat-token-leaked,internal-api,legacy-cli,incompatible-with-uc,notebooks-too-many-cells,notebooks-percent-run,spark-outside-function,use-display-instead-of-show,no-spark-argument-in-function .
```

[[back to top](#databricks-labs-pylint-plugin)]

<!-- END CHECKS -->

# Project Support

Please note that this project is provided for your exploration only and is not 
formally supported by Databricks with Service Level Agreements (SLAs). They are 
provided AS-IS, and we do not make any guarantees of any kind. Please do not 
submit a support ticket relating to any issues arising from the use of this project.

Any issues discovered through the use of this project should be filed as GitHub 
[Issues on this repository](https://github.com/databrickslabs/pylint-plugin/issues). 
They will be reviewed as time permits, but no formal SLAs for support exist.
