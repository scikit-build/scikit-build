
cpdef void hello(str strArg):
    "Prints back 'Hello <param>', for example example: hello.hello('you')"
    print("Hello, {}!".format(strArg))

cpdef long elevation():
    "Returns elevation of Nevado Sajama."
    return 21463L
