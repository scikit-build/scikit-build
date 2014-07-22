This folder contains tests of PyCMake itself - not projects that use
PyCMake.  Test projects should go in the test_projects folder, with
the idea that PyCMake will be installed before running those tests.

This is required because testing projects entails installing them,
which depends on having PyCMake available to the system's Python for
installation purposes.
