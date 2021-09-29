
import os
import pytest

from path import Path

from . import initialize_git_repo_and_commit, prepare_project

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../dist'))

# Test if package can be imported to allow testing on
# conda-forge where ``pytest-virtualenv`` is not available.
pytest.importorskip("pytest_virtualenv",
                    reason="pytest_virtualenv not available. See #228")


def test_source_distribution(virtualenv):
    sdists = Path(DIST_DIR).files(match="*.tar.gz") if Path(DIST_DIR).exists() else []
    if not sdists:
        pytest.skip("no source distribution available")
    assert len(sdists) == 1

    virtualenv.run("pip install %s" % sdists[0])
    assert "scikit-build" in virtualenv.installed_packages()

    prepare_project("hello-no-language", virtualenv.workspace, force=True)
    initialize_git_repo_and_commit(virtualenv.workspace, verbose=False)

    virtualenv.run("python setup.py bdist_wheel")


def test_wheel(virtualenv):
    wheels = Path(DIST_DIR).files(match="*.whl") if Path(DIST_DIR).exists() else []
    if not wheels:
        pytest.skip("no wheel available")
    assert len(wheels) == 1

    virtualenv.run("pip install %s" % wheels[0])
    assert "scikit-build" in virtualenv.installed_packages()

    prepare_project("hello-no-language", virtualenv.workspace, force=True)
    initialize_git_repo_and_commit(virtualenv.workspace, verbose=False)

    virtualenv.run("python setup.py bdist_wheel")
