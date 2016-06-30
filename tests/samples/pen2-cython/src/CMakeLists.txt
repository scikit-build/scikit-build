
# add_cython_target(_pen2)
add_cython_target(_pen2 OUTPUT_VAR X)
add_library(_pen2 MODULE ${X})
python_extension_module(_pen2)

install(TARGETS _pen2 LIBRARY DESTINATION src)
install(FILES __main__.py DESTINATION src)
install(FILES __init__.py DESTINATION src)

