
add_cython_target(_pen2)
add_library(_pen2 MODULE ${_pen2})
python_extension_module(_pen2)

INSTALL(TARGETS _pen2 LIBRARY DESTINATION src)
INSTALL(FILES __main__.py DESTINATION src)
INSTALL(FILES __init__.py DESTINATION src)

