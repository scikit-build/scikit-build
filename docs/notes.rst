=====
Notes
=====

``sysconfig`` vs ``distutils.sysconfig``
----------------------------------------

After installing CPython, two sysconfig modules are available:

* ``sysconfig``
* ``distutils.sysconfig``

A difference is the value associated with the ``EXT_SUFFIX`` and ``SO`` configuration
variables.

.. table::

    +----------------+-------------------------+----------------------------------+------------------------+---------------------+
    |                |                         | Linux                            | macOS                  | Windows             |
    +----------------+-------------------------+----------------------------------+------------------------+---------------------+
    |                |                         | CPython 2.7                                                                     |
    +================+=========================+==================================+========================+=====================+
    | **SO**         | **sysconfig**           | .so                              | .so                    | .pyd                |
    |                +-------------------------+                                  |                        |                     |
    |                | **distutils.sysconfig** |                                  |                        |                     |
    +----------------+-------------------------+----------------------------------+------------------------+---------------------+
    | **EXT_SUFFIX** | **sysconfig**           | None                             | None                   | None                |
    |                +-------------------------+                                  |                        |                     |
    |                | **distutils.sysconfig** |                                  |                        |                     |
    +----------------+-------------------------+----------------------------------+------------------------+---------------------+
    |                |                         | **CPython >= 3.5**                                                              |
    +----------------+-------------------------+----------------------------------+------------------------+---------------------+
    | **SO**         | **sysconfig**           | .cpython-37m-x86_64-linux-gnu.so | .cpython-37m-darwin.so | .pyd                |
    |                +-------------------------+                                  |                        +---------------------+
    |                | **distutils.sysconfig** |                                  |                        | .cp37-win_amd64.pyd |
    +----------------+-------------------------+                                  |                        +---------------------+
    | **EXT_SUFFIX** | **sysconfig**           |                                  |                        | .pyd                |
    |                +-------------------------+                                  |                        +---------------------+
    |                | **distutils.sysconfig** |                                  |                        | .cp37-win_amd64.pyd |
    +----------------+-------------------------+----------------------------------+------------------------+---------------------+



.. note::

    The ``EXT_SUFFIX`` was introduced in Python 3.4 and is functionally equivalent to ``SO``
    configuration variable. The ``SO`` configuration variable has been deprecated since Python 3.4.

.. note::

    The information reported in the table have been collected execution the following python snippet.

    .. code-block:: python

        def display_ext_suffix_config_var():
            import platform
            import sys
            import sysconfig
            from distutils import sysconfig as du_sysconfig

            details = (platform.python_implementation(),) + sys.version_info[:3]
            print("%s %s.%s.%s" % details)
            print(" SO")
            print("  sysconfig           : %s" % sysconfig.get_config_var("SO"))
            print("  distutils.sysconfig : %s" % du_sysconfig.get_config_var("SO"))
            print(" EXT_SUFFIX")
            print("  sysconfig           : %s" % sysconfig.get_config_var("EXT_SUFFIX"))
            print("  distutils.sysconfig : %s" % du_sysconfig.get_config_var("EXT_SUFFIX"))


        display_ext_suffix_config_var()
