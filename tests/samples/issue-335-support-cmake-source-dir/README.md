[![Build Status](https://travis-ci.org/massich/replicate_pytime_timeval_error.svg?branch=master)](https://travis-ci.org/massich/replicate_pytime_timeval_error)
[![Build status](https://ci.appveyor.com/api/projects/status/l541a07x31dce25y/branch/master?svg=true)](https://ci.appveyor.com/project/massich/replicate-pytime-timeval-error/branch/master)


# replicate_pytime_timeval_error
This is a MWE to replicate this issue https://github.com/openmeeg/openmeeg/issues/312

## Requirments
* cmake >= 3.2

## How to run it
```sh
mkdir build
cd build
cmake .. && cmake --build . && ctest -v .
```
