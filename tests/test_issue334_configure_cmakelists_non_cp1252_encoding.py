from __future__ import annotations

import pytest

from . import project_setup_py_test


@pytest.mark.deprecated()
@project_setup_py_test("issue-334-configure-cmakelist-non-cp1252-encoding", ["install"], disable_languages_test=True)
def test_install_command():
    pass
