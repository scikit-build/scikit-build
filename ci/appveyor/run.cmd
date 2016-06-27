@ECHO OFF
@SETLOCAL enableextensions enabledelayedexpansion

IF "x%SKIP%"=="x0" (
    IF NOT "x%CMAKE_GENERATOR:Visual Studio=%"=="x%CMAKE_GENERATOR%" (
        echo cmd /E:ON /V:ON /C ci\appveyor\run-with-visual-studio.cmd %*
        cmd /E:ON /V:ON /C ci\appveyor\run-with-visual-studio.cmd %*
    )

    IF NOT "x%CMAKE_GENERATOR:MinGW Makefiles=%"=="x%CMAKE_GENERATOR%" (
        echo cmd /E:ON /V:ON /C ci\appveyor\run-with-mingw.cmd %*
        cmd /E:ON /V:ON /C ci\appveyor\run-with-mingw.cmd %*
    )
) ELSE (
    ECHO SKIPPING: %*
)

ENDLOCAL
