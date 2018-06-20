import glob
import os
import tarfile
import wheel

from pkg_resources import parse_version
from zipfile import ZipFile

from skbuild.utils import to_unix_path

from . import project_setup_py_test


def check_whls(project_name):
    whls = glob.glob('dist/*.whl')
    assert len(whls) == 1
    assert not whls[0].endswith('-none-any.whl')

    expected_content = [
        '%s.dist-info/top_level.txt' % project_name,
        '%s.dist-info/WHEEL' % project_name,
        '%s.dist-info/RECORD' % project_name,
        '%s.dist-info/METADATA' % project_name,
        'hello/__init__.py',
        'hello/cmake_generated_module.py',
        'hello/data/subdata/hello_data1_include_from_manifest.txt',
        'hello/data/subdata/hello_data2_include_from_manifest.txt',
        'hello/data/subdata/hello_data3_cmake_generated.txt',
        'hello/hello_data1_cmake_generated.txt',
        'hello/hello_data2_cmake_generated.txt',
        'hello/hello_include_from_manifest.txt',
        'hello2/__init__.py',
        'hello2/hello2_data1_cmake_generated.txt',
        'hello2/hello2_data2_cmake_generated.txt',
        'hello2/data2/subdata2/hello2_data3_cmake_generated.txt',
        'hello2/data2/subdata2/hello2_data1_include_from_manifest.txt',
        'hello2/data2/subdata2/hello2_data2_include_from_manifest.txt',
        'hello2/hello2_include_from_manifest.txt',
    ]
    if parse_version(wheel.__version__) < parse_version('0.31.0'):
        expected_content += [
            '%s.dist-info/DESCRIPTION.rst' % project_name,
            '%s.dist-info/metadata.json' % project_name
        ]

    archive = ZipFile(whls[0])
    member_list = archive.namelist()
    assert sorted(expected_content) == sorted(member_list)


def check_sdist(proj, base=''):
    sdists_tar = glob.glob('dist/*.tar.gz')
    sdists_zip = glob.glob('dist/*.zip')
    assert sdists_tar or sdists_zip

    expected_content = [
        to_unix_path(os.path.join(proj, 'setup.py')),
        to_unix_path(os.path.join(proj, base, 'hello/__init__.py')),
        to_unix_path(os.path.join(proj, base, 'hello/data/subdata/hello_data1_include_from_manifest.txt')),
        to_unix_path(os.path.join(proj, base, 'hello/data/subdata/hello_data2_include_from_manifest.txt')),
        to_unix_path(os.path.join(
            proj, base, 'hello/data/subdata/hello_data4_include_from_manifest_and_exclude_from_setup.txt')),
        to_unix_path(os.path.join(proj, base, 'hello/hello_include_from_manifest.txt')),
        to_unix_path(os.path.join(proj, base, 'hello2/__init__.py')),
        to_unix_path(os.path.join(proj, base, 'hello2/data2/subdata2/hello2_data1_include_from_manifest.txt')),
        to_unix_path(os.path.join(proj, base, 'hello2/data2/subdata2/hello2_data2_include_from_manifest.txt')),
        to_unix_path(os.path.join(
            proj, base, 'hello2/data2/subdata2/hello2_data4_include_from_manifest_and_exclude_from_setup.txt')),
        to_unix_path(os.path.join(proj, base, 'hello2/hello2_include_from_manifest.txt')),
        to_unix_path(os.path.join(proj, 'PKG-INFO'))
    ]

    member_list = None
    if sdists_tar:
        if base != '':
            expected_content.extend([to_unix_path(os.path.join(proj, base))])
        expected_content.extend([
            proj,
            to_unix_path(os.path.join(proj, base, 'hello')),
            to_unix_path(os.path.join(proj, base, 'hello/data')),
            to_unix_path(os.path.join(proj, base, 'hello/data/subdata')),
            to_unix_path(os.path.join(proj, base, 'hello2')),
            to_unix_path(os.path.join(proj, base, 'hello2/data2')),
            to_unix_path(os.path.join(proj, base, 'hello2/data2/subdata2'))
        ])
        member_list = tarfile.open('dist/%s.tar.gz' % proj).getnames()

    elif sdists_zip:
        member_list = ZipFile('dist/%s.zip' % proj).namelist()

    assert expected_content and member_list
    assert sorted(expected_content) == sorted(member_list)


@project_setup_py_test("test-include-exclude-data", ["bdist_wheel"])
def test_include_exclude_data():
    check_whls('test_include_exclude_data-0.1.0')


@project_setup_py_test("test-include-exclude-data", ["sdist"])
def test_hello_sdist():
    check_sdist('test_include_exclude_data-0.1.0')


@project_setup_py_test("test-include-exclude-data-with-base", ["bdist_wheel"])
def test_include_exclude_data_with_base():
    check_whls('test_include_exclude_data_with_base-0.1.0')


@project_setup_py_test("test-include-exclude-data-with-base", ["sdist"])
def test_hello_sdist_with_base():
    check_sdist('test_include_exclude_data_with_base-0.1.0', base='src')
