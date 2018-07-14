#include <iostream>
#include "bar.h"
#include "foo.h"

void foo_hello()
{
    std::cout << "Hello from foo" << std::endl;
}

void link_bar_hello()
{
    bar_hello();
}
