
@ECHO OFF

SET COMMAND_TO_RUN=%*
SET MINGW_ROOT=C:\MinGW

ECHO Using default MinGW build environment
SET PATH=%MINGW_ROOT%\bin;%PATH%
ECHO Executing: %COMMAND_TO_RUN%
call %COMMAND_TO_RUN% || EXIT 1

