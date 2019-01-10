
import os
import sysconfig

from distutils import sysconfig as du_sysconfig

from . import project_setup_py_test


@project_setup_py_test("issue-284-build-ext-inplace", ["build_ext", "--inplace"], disable_languages_test=True)
def test_build_ext_inplace_command():
    assert os.path.exists('hello/_hello_sk%s' % sysconfig.get_config_var('SO'))

    # See issue scikit-build #383
    assert os.path.exists('hello/_hello_ext%s' % du_sysconfig.get_config_var('SO'))
