from __future__ import annotations

import pytest

from . import (
    project_setup_py_test,
)


@pytest.mark.deprecated()
@project_setup_py_test("issue-274-support-default-package-dir", ["install"], disable_languages_test=True)
def test_install_command():
    pass
