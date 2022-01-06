"""
Scikit-Build's Helper API

The goal of this API is to provide utilities which ease the process of creating
and maintaining a setup.py script. To see how this API can make writing a
`setup.py` easier, consider the following example.

Example:
    >>> # xdoctest: +SKIP
    >>> import skbuild
    >>> import os
    >>> package = 'mymodule'
    >>> version = skbuild.parse_version(package + '/__init__.py')
    >>> if __name__ == '__main__':
    >>>     setup(
    >>>         name=package,
    >>>         version=version,
    >>>         author=', '.join(skbuild.parse_authors()),
    >>>         description='A short little blurb',
    >>>         long_description=skbuild.parse_long_description(),
    >>>         install_requires=skbuild.parse_requirements('requirements.txt'),
    >>>         extras_require={
    >>>             'dev': parse_requirements('requirements-dev.txt'),
    >>>             'docs': parse_requirements('requirements-docs.txt'),
    >>>         },
    >>>         author_email='you@email.com',
    >>>         url='https://github.com/you/mymodule',
    >>>         license='YOUR LICENCE',
    >>>         packages=skbuild.find_packages(include=package + '.*'),
    >>>         classifiers=[
    >>>             'Development Status :: 4 - Beta',
    >>>             'Intended Audience :: Developers',
    >>>             'Topic :: Software Development :: Libraries :: Python Modules',
    >>>             'Programming Language :: Python :: 3',
    >>>         ],
    >>>     )
"""
import ast
import re
from os.path import exists
from os.path import join
from os.path import sys


__all__ = ['find_packages', 'parse_authors', 'parse_long_description',
           'parse_requirements', 'parse_version']


# Inherit some useful tools from setutools
def find_packages(where='.', exclude=(), include=('*',)):
    """
    Runs `setuptools.fine_packages`

    Args:
        where (PathLike):
            is the root directory which will be searched for packages.  It
            should be supplied as a "cross-platform" (i.e. URL-style) path; it
            will be converted to the appropriate local path syntax.

        exclude (Sequence):
            is a sequence of package names to exclude; '*' can be used as a
            wildcard in the names, such that 'foo.*' will exclude all
            subpackages of 'foo' (but not 'foo' itself).

        include (Sequence):
            is a sequence of package names to include.  If it's specified, only the
            named packages will be included.  If it's not specified, all found
            packages will be included.  'include' can contain shell style wildcard
            patterns just like 'exclude'.

    Returns:
        List[str]: a list all Python packages found within directory 'where'
    """
    from setuptools import find_packages
    return find_packages(where, exclude, include)


def parse_version(fpath=None, sourcecode=None):
    """
    Statically parse the version number from a source file.

    This is meant to be used for parsing the version attribute in the your
    module's root `__init__.py` file. This information should then passed to
    the `version` argument of `setup`.

    Args:
        fpath (str): path to the file that contains the __version__ attribute.
        sourcecode (str, default=None): overrides the text that is parsed

    Notes:
        This function is implemented using static analysis, which means that
        this will not work for version strings that are built dynamically.

    Example:
        >>> sourcecode = '__version__ = "0.0.1"'
        >>> parse_version(sourcecode=sourcecode)
        0.0.1
    """
    if sourcecode is None:
        if fpath is None:
            raise ValueError('must specify fpath if sourcecode is None')
        with open(fpath) as file_:
            sourcecode = file_.read()

    # The advantage of using an AST to statically parse values is that setup.py
    # wont need to import your module. AST is also more robust than regex based
    # parsers.
    pt = ast.parse(sourcecode)
    class VersionVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            for target in node.targets:
                if getattr(target, 'id', None) == '__version__':
                    self.version = node.value.s
    visitor = VersionVisitor()
    visitor.visit(pt)
    return visitor.version


def parse_long_description(fpath='README.rst'):
    """
    Parse the description in the README file

    Used for parsing the readme and passing it to the `long_description`
    argument of `skbuild.setup`. If the specified file doesn't exist then the
    empty string is returned. This ensures the setup works in bare bones
    installs where the readme might not exist.

    Args:
        fpath (PathLike): path to the readme file.

    Returns:
        str: contents of readme or the empty string if the file doesn't exist
    """
    # This breaks on pip install, so check that it exists.
    if exists(fpath):
        with open(fpath, 'r') as file:
            text = file.read()
        return text
    return ''


def parse_authors():
    """
    Parse the git authors of a repo

    Returns:
        List[str]: list of authors
    """
    import subprocess
    try:
        out = subprocess.check_output(['git', 'shortlog', '-s'],
                                      universal_newlines=True)
    except Exception as ex:
        print('ex = {!r}'.format(ex))
        return []
    else:
        striped_lines = (l.strip() for l in out.split('\n'))
        freq_authors = [line.split(None, 1) for line in striped_lines if line]
        freq_authors = sorted((int(f), a) for f, a in freq_authors)[::-1]
        # keep authors with uppercase letters
        authors = [a for f, a in freq_authors if a.lower() != a]
        return authors


def parse_requirements(fpath='requirements.txt', text=None):
    """
    Parse the package dependencies listed in a requirements file but strips
    specific versioning information. This can then be passed to `skbuild.setup`
    via the arguments: `install_requires` and `extras_require['all']`.

    Args:
        fpath (PathLike): path to the requirements file
        text (str, default=None): overrides the text that is parsed

    Returns:
        List[str]: output suitable for `install_requires`

    Example:
        >>> text = ('''
            Cython >= 0.28.4
            pyqt5>= 5.11.2;python_version>'2.7'
            numpy >= 1.16.4
            -e git+ssh://git@github.com:scikit-build/scikit-build.git#egg=skbuild
            # xxhash
        >>> ''')
        >>> parse_requirements(text=text)
        ['Cython', "pyqt5;python_version>'2.7'", 'numpy', 'skbuild']
    """

    if text is not None:
        lines = text.splitlines()
    elif exists(fpath):
        lines = list(open(fpath, 'r').readlines())

    packages = []
    for info in _parse_requirement_lines(lines):
        package = info['package']
        if not sys.version.startswith('3.4'):
            # apparently package_deps are broken in 3.4
            platform_deps = info.get('platform_deps')
            if platform_deps is not None:
                package += ';' + platform_deps
        packages.append(package)
    return packages


def _parse_requirements_line(line):
    """
    Parse a single line from a requirements file and return a dictionary of
    information. Lines starting with `-r` may produce multiple results.
    """
    if line.startswith('-r '):
        # Allow specifying requirements in other files
        target_fpath = line.split(' ')[1]
        lines = list(open(target_fpath, 'r').readlines())
        for info in _parse_requirement_lines(lines):
            yield info
    elif line.startswith('-e '):
        info = {}
        info['package'] = line.split('#egg=')[1]
        yield info
    else:
        # Remove versioning from the package
        pat = '(' + '|'.join(['>=', '==', '>']) + ')'
        parts = re.split(pat, line, maxsplit=1)
        parts = [p.strip() for p in parts]

        info = {}
        info['package'] = parts[0]
        if len(parts) > 1:
            op, rest = parts[1:]
            if ';' in rest:
                # Handle platform specific dependencies
                # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                version, platform_deps = map(str.strip, rest.split(';'))
                info['platform_deps'] = platform_deps
            else:
                version = rest
            info['version'] = (op, version)
        yield info


def _parse_requirement_lines(lines):
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            for info in _parse_requirements_line(line):
                yield info
