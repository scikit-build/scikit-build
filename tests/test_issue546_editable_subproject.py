import os
import shutil

DIR = os.path.abspath(os.path.dirname(__file__))
EDITABLE_SUBPROJECT = os.path.join(DIR, "samples/issue-546-editable-subproject")


def test_classic_subproject(virtualenv):
    skbuild_dir = os.path.join(DIR, "_skbuild")
    if os.path.exists(skbuild_dir):
        shutil.rmtree(skbuild_dir)

    virtualenv.run("python -m pip install .", cwd=EDITABLE_SUBPROJECT)
    virtualenv.run('python -c "import pkg"')
    virtualenv.run('python -c "import pkg.subpkg"')


def test_editable_subproject(virtualenv):
    skbuild_dir = os.path.join(DIR, "_skbuild")
    if os.path.exists(skbuild_dir):
        shutil.rmtree(skbuild_dir)

    virtualenv.run("python -m pip install scikit-build cmake pybind11")
    virtualenv.run("python -m pip install --no-build-isolation -e .", cwd=EDITABLE_SUBPROJECT)
    virtualenv.run('python -c "import pkg"')
    virtualenv.run('python -c "import pkg.subpkg"')
