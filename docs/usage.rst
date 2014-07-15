========
Usage
========

To use PyCMake in a project::

	# in your project's setup.py file, instead of from distutils import setup
	from pycmake.distutils_wrap import setup

TODO (PyCMake developer): need to provide small, self-contained setup function calls for (at least) 2 use cases: when a CMakeLists.txt file already exists, and when users want PyCMake to create a CMakeLists.txt file based on specifying some input files.

Alternatively, you can drive CMake more directly yourself with PyCMake::
    
    # cmaker defines an object that provides convenient access to CMake configure & build functionality
    from pycmake import cmaker
    maker = cmaker.CMaker()
    # based on CMakeLists.txt file in current directory, generates Makefiles, Visual Studio solutions, or whatever is appropriate for your platform
    maker.configure()
    # executes the build with the appropriate build tool and performs installation to local folders
    maker.make()