from __future__ import annotations

import pytest


@pytest.mark.deprecated
def test_install_command(project_setup_py_test):
    with project_setup_py_test("issue-274-support-default-package-dir", ["install"], disable_languages_test=True):
        pass
