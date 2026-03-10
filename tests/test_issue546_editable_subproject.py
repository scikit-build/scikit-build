import os

DIR = os.path.abspath(os.path.dirname(__file__))


def test_editable_subproject(virtualenv):
    virtualenv.run("pip install -e {DIR}/samples/issue-546-editable-subproject".format(DIR=DIR))
    virtualenv.run('python -c "import example.tools"')
