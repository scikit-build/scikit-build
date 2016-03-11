========
Usage
========

To use scikit-build in a project::

	# in your project's setup.py file, instead of from distutils import setup
	from skbuild.distutils_wrap import setup

TODO (scikit-build developer): need to provide small, self-contained setup
function calls for (at least) 2 use cases: when a CMakeLists.txt file already
exists, and when users want scikit-build to create a CMakeLists.txt file based
on specifying some input files.

Alternatively, you can drive CMake more directly yourself with scikit-build::
    
    # cmaker defines an object that provides convenient access to CMake configure & build functionality
    from skbuild import cmaker
    maker = cmaker.CMaker()
    # based on CMakeLists.txt file in current directory, generates Makefiles, Visual Studio solutions, or whatever is appropriate for your platform
    maker.configure()
    # executes the build with the appropriate build tool and performs installation to local folders
    maker.make()
