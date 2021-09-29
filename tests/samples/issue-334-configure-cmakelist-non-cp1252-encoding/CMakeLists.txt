cmake_minimum_required(VERSION 3.5.0)
project(foobar NONE)

# Sanskrit for "I can eat glass, it does not hurt me"
# See http://kermitproject.org/utf8.html
install(CODE "execute_process(COMMAND ${CMAKE_COMMAND} -E echo \"kācaṃ śaknomyattum; nopahinasti mām\")")
