
def execute(code, _globals, _locals):
    exec code in _globals, _locals # flake8: noqa: E901: SyntaxError
