from __future__ import annotations

import pytest

from . import egg_install_incompatible


@pytest.mark.deprecated
@pytest.mark.skipif(
    egg_install_incompatible(), reason="pkg_resources rejects eggs built for an older macOS major version"
)
def test_install_command(project_setup_py_test):
    with project_setup_py_test("issue-274-support-default-package-dir", ["install"]):
        pass
