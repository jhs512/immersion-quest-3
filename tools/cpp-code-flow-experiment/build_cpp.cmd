@echo off
rem Experiment only (MQ has no C++ course or grader): build main.cpp with the installed MSVC and a PDB.
rem usage: build_cpp.cmd <dir with main.cpp>
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cd /d "%~1" || exit /b 1
cl /nologo /utf-8 /std:c++17 /EHsc /Zi /Od /Ob0 /RTC1 /MDd main.cpp "%~dp0mq_unbuffered.c" /Fe:main_cpp.exe /Fd:main_cpp.pdb /link /INCREMENTAL:NO
