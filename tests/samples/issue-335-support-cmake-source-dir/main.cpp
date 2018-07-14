#include <iostream>
#include "foo.h"

int main(int argc, char* argv[])
{
  std::cout << "Hello from main" << std::endl;
  foo_hello();
  link_bar_hello();

  return 0;
}

