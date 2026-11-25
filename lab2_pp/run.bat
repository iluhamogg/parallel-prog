@echo off
setlocal
cd /d "%~dp0"
where cl >nul 2>&1
if errorlevel 1 (
  set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
  if not exist "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" goto fail
  for /f "usebackq delims=" %%i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do call "%%i\VC\Auxiliary\Build\vcvars64.bat"
)
where cl >nul 2>&1 || goto fail
cl /nologo /EHsc /O2 /std:c++17 /openmp main.cpp /Fe:matrix.exe || goto fail
py -m pip install -r requirements.txt || goto fail
py experiment.py --exe .\matrix.exe --environment "Windows 11; AMD Ryzen 9 7940HS; 8 physical cores; 16 logical processors; 16 GB RAM; MSVC /O2 /openmp" || goto fail
echo Completed. See README.md and results.
pause
exit /b 0
:fail
echo Failed. Check Python and Visual Studio C++ desktop development tools.
pause
exit /b 1
