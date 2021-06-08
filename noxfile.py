import nox

nox.options.sessions = ["lint", "tests"]

PYTHON_ALL_VERSIONS = ["2.7", "3.5", "3.6", "3.7", "3.8", "3.9"]


@nox.session
def lint(session):
    session.install("flake8")
    session.run("flake8")


@nox.session(python=PYTHON_ALL_VERSIONS)
def tests(session):
    """
    Run the tests.
    """
    session.install(".[test]")
    session.run("pytest", *session.posargs)


@nox.session
def docs(session):
    """
    Build the docs.
    """

    session.install("-r", "requirements-docs.txt")
    session.install(".")

    session.chdir("docs")
    session.run("sphinx-build", "-M", "html", ".", "_build")

    if session.posargs:
        if "serve" in session.posargs:
            print("Launching docs at http://localhost:8000/ - use Ctrl-C to quit")
            session.run("python", "-m", "http.server", "8000", "-d", "_build/html")
        else:
            print("Unsupported argument to docs")


@nox.session
def build(session):
    """
    Make an SDist and a wheel.
    """

    session.install("build")
    session.run("python", "-m", "build")
