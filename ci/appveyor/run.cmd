@ECHO OFF
@SETLOCAL enableextensions enabledelayedexpansion

IF "x%SKIP%"=="x1" (
    ECHO SKIPPING: %*
    GOTO done
)

IF NOT DEFINED CMAKE_GENERATOR ( GOTO vstudio )
IF NOT "x%CMAKE_GENERATOR:MinGW=%"=="x%CMAKE_GENERATOR%" ( GOTO mingw )

:vstudio
    SET script=ci\appveyor\run-with-visual-studio.cmd
    GOTO run

:mingw
    SET script=ci\appveyor\run-with-mingw.cmd
    GOTO run

:run
    echo cmd /E:ON /V:ON /C %script% %*
    cmd /E:ON /V:ON /C %script% %* || EXIT 1

:done

ENDLOCAL
