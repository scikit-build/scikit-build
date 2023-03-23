from libc.stdio cimport printf


cpdef void hello(str strArg):
    "Prints back 'Hello <param>', for example example: hello.hello('you')"
    printf("Hello, %s! :)\n", <char*>strArg)
