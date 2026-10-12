@echo off
rem Set up the course on Windows. Everything runs inside WSL 2 (Ubuntu recommended).
rem   .\setup            use the default WSL distribution
rem   set COURSE_WSL_DISTRO=Ubuntu-24.04 ^& .\setup    choose a distribution
setlocal
where wsl.exe >nul 2>&1
if errorlevel 1 (
  echo WSL 2 is required on Windows. In an Administrator PowerShell run:  wsl --install -d Ubuntu
  echo Then restart, open Ubuntu once to create your user, and run .\setup again.
  exit /b 1
)
set "DISTRO=%COURSE_WSL_DISTRO%"
if defined DISTRO (
  wsl.exe -d %DISTRO% --cd "%~dp0." --exec bash ./setup.sh %*
) else (
  wsl.exe --cd "%~dp0." --exec bash ./setup.sh %*
)
exit /b %ERRORLEVEL%
