@echo off
rem Run a lab from Windows through WSL:  .\lab list   .\lab 08/L01   .\lab 08/L01 action_noise=0.3   .\lab doctor
setlocal
set "DISTRO=%COURSE_WSL_DISTRO%"
if not defined DISTRO if exist "%~dp0.course\wsl-distro.txt" set /p DISTRO=<"%~dp0.course\wsl-distro.txt"
if defined DISTRO (
  wsl.exe -d %DISTRO% --cd "%~dp0." --exec bash ./lab.sh %*
) else (
  wsl.exe --cd "%~dp0." --exec bash ./lab.sh %*
)
exit /b %ERRORLEVEL%
