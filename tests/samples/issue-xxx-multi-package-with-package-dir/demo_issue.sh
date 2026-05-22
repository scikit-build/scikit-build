
run_common_module_tests(){
    echo "Running common tests of the installed module"

    echo "Package Version: $(python -c 'import my_skb_mod; print(my_skb_mod.__version__)')"
    echo "Python Package Location: $(python -c 'import my_skb_mod; print(my_skb_mod.__file__)')"
    echo "Compiled Cython Module: $(python -c 'from my_skb_mod import _myalgo_cython; print(_myalgo_cython.__file__)')"
    # Test that we can access the module resource
    python -c "import my_skb_mod; print(my_skb_mod.submod.get_module_resouce())"

    echo "Finished common tests of the installed module"

    python -c "import my_skb_mod; print(my_skb_mod.__doc__)"


}


#######################
# WHEEL MODE TEST
#######################

# First test with a regular wheel
pip wheel .
WHEEL_FPATH="$(ls my_skb_mod-*.whl)"
echo "WHEEL_FPATH = $WHEEL_FPATH"
# Should see the submodule resource here, but we don't
unzip -l "$WHEEL_FPATH"

# Install the wheel
pip uninstall -y "my_skb_mod" || echo "already uninstalled"
pip install "$WHEEL_FPATH"

# Run the module tests
# This does not include the package data correctly
run_common_module_tests


#######################
# DEVELOPMENT MODE TEST
#######################

# Clean up
pip uninstall -y "my_skb_mod" || echo "already uninstalled"
rm -rf _skbuild || echo "already clean"
rm -rf src/python/my_skb_mod/*.so || echo "already clean"

# Test in development mode
# FIXME: running ``pip install -e .`` multiple times breaks!
pip install --verbose -e .

# The egg link should point to
# .../issue-xxx-multi-package-with-package-dir/src/python
#
# NOT
#
# .../issue-xxx-multi-package-with-package-dir/
SITE_PACKAGE_DPATH="$(python -c 'import distutils.sysconfig; print(distutils.sysconfig.get_python_lib())')"
echo "SITE_PACKAGE_DPATH = $SITE_PACKAGE_DPATH"
cat "$SITE_PACKAGE_DPATH/my_skb_mod.egg-link"
# but even with the packages=[''] hack, there seems to be an extra ../../.. term
# not sure what's going on.

run_common_module_tests



#######################
# DEMO MULTIPLE EDIBALE PIP INSTALL ISSUE
#######################

# Maybe this isn't an issue here? It is an issue in the project I'm basing this
# on cant run this command multiple times. I dont know why.
# This only seeps to break if the "packages" directory is specified as
# `packages=['my_skb_mod']`. Otherwise it does seem to work
pip uninstall -y "my_skb_mod" || echo "already uninstalled"
pip uninstall -y "my_skb_mod" || echo "already uninstalled"
pip install -e .
pip install -e .
