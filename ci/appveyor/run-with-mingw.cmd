
@ECHO OFF

SET COMMAND_TO_RUN=%*
SET MINGW_ROOT=C:\MinGW

ECHO Using default MinGW build environment
SET PATH=%MINGW_ROOT%\bin;%PATH%


:: workaround for MinGW Make insisting on using sh.exe if it's in the PATH
::
:: Explanation:
::
::   Root Cause
::   ----------
::   Appveyor starts tests with an environment that includes GIT and everything
::   it needs on your PATH. This includes a copy of sh.exe. Presumably, appveyor
::   needs git to perform the project checkout, and they probably want to keep
::   GIT on the PATH in case your project needs to run some other git commands.
::
::   The true root cause of the issue is MinGW Make insisting on running
::   commands with sh if it is in your PATH, which will not work with Makefiles
::   generated using the MinGW Makefile generator in CMake. The only way to
::   force MinGW Make to run using cmd.exe is to explicitly remove any directory
::   with an executable sh from the PATH.
::
::   Fix in CMake?
::   -------------
::   Not wanting to meddle with a user's environment (let alone their PATH)
::   seems like a good reason for a CMake maintainer to leave the issue as-is,
::   especially considering that this is only a problem for Windows users who
::   have deliberately added coreutils to their PATH (like in appveyor) and the
::   simplest solution in this case is to just use a different generator.
::
::   Fix in Appveyor?
::   ----------------
::   On the other hand, keeping a functional git environment in a user's PATH
::   from the outset seems like a more important feature to a member of the
::   Appveyor support staff than catering to the specific needs of CMake users,
::   or anyone who needs to use MinGW over Visual Studio, for that matter.
::
::   So, it is likely we will need to maintain this work-around.
::
:: Links:
::
:: CMake Bug #7870: https://cmake.org/Bug/view.php?id=7870
:: CMake Wiki Page: https://cmake.org/Wiki/CMake_MinGW_Compiler_Issues
:: AppVeyor Issue #3193: http://help.appveyor.com/discussions/problems/
::                           3193-cmake-building-for-mingw-issue-with-git-shexe

set PATH=%PATH:C:\Program Files\Git\usr\bin;=%
set PATH=%PATH:C:\Program Files (x86)\Git\usr\bin;=%
set PATH=%PATH:C:\Program Files\Git\bin;=%
set PATH=%PATH:C:\Program Files (x86)\Git\bin;=%
set PATH=%PATH:C:\Program Files\Git\cmd;=%
set PATH=%PATH:C:\Program Files (x86)\Git\cmd;=%


ECHO Executing: %COMMAND_TO_RUN%
call %COMMAND_TO_RUN% || EXIT 1

