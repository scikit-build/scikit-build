
@ECHO OFF

SET COMMAND_TO_RUN=%*
SET MINGW_ROOT=C:\MinGW

ECHO Using default MinGW build environment
SET PATH=%MINGW_ROOT%\bin;%PATH%


:: workaround for CMake not wanting sh.exe on PATH for MinGW

set PATH=%PATH:C:\Program Files\Git\usr\bin;=%
set PATH=%PATH:C:\Program Files (x86)\Git\usr\bin;=%
set PATH=%PATH:C:\Program Files\Git\bin;=%
set PATH=%PATH:C:\Program Files (x86)\Git\bin;=%
set PATH=%PATH:C:\Program Files\Git\cmd;=%
set PATH=%PATH:C:\Program Files (x86)\Git\cmd;=%


ECHO Executing: %COMMAND_TO_RUN%
call %COMMAND_TO_RUN% || EXIT 1

