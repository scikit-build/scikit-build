import os


def which(name, flags=os.X_OK):
    """Analogue of unix 'which'. Borrowed from the Twisted project, see
    their licence here: https://twistedmatrix.com/trac/browser/trunk/LICENSE

    Copied from ``pytest_shutil.cmdline.which`` to allow testing on
    conda-forge where ``pytest-shutil`` is not available.
    """
    result = []
    exts = filter(None, os.environ.get("PATHEXT", "").split(os.pathsep))
    path = os.environ.get("PATH", None)
    if path is None:
        return []
    for p in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                result.append(pext)
    return result
