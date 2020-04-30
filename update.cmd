@echo off
setlocal EnableDelayedExpansion
set src_7z=%~1
set dest_path=%~2

set SEVENZIP=
where 7z > nul 2>&1
if not errorlevel 1 (
    set SEVENZIP=7z
    goto done_sevenzip
)

where 7za > nul 2>&1
if not errorlevel 1 (
    set SEVENZIP=7za
    goto done_sevenzip
)

for /f "tokens=3,*" %%v in ('reg query HKLM\Software\7-Zip /v Path64') do (
    if exist "%%v %%w7z.exe" (
        set "SEVENZIP=%%v %%w7z.exe"
        goto done_sevenzip
    )
    if exist "%%v %%w7za.exe" (
        set "SEVENZIP=%%v %%w7za.exe"
        goto done_sevenzip
    )
)

for /f "tokens=3,*" %%v in ('reg query HKLM\Software\7-Zip /v Path') do (
    if exist "%%v %%w7z.exe" (
        set "SEVENZIP=%%v %%w7z.exe"
        goto done_sevenzip
    )
    if exist "%%v %%w7za.exe" (
        set "SEVENZIP=%%v %%w7za.exe"
        goto done_sevenzip
    )
)

set WINRAR=
where winrar > nul 2>&1
if not errorlevel 1 (
    set WINRAR=winrar
    goto done_winrar
)

for /f "tokens=3,*" %%v in ('reg query HKLM\Software\WinRAR /v exe64') do (
    set "WINRAR=%%v %%w"
    goto done_winrar
)

for /f "tokens=3,*" %%v in ('reg query HKLM\Software\WOW6432Node\WinRAR /v exe32') do (
    set "WINRAR=%%v %%w"
    goto done_winrar
)


if not defined SEVENZIP (
    if not defined WINRAR (
        echo 7zip and WinRAR not found
        pause
        exit /b 1
    )
)


:done_sevenzip
for /f %%f in ("%src_7z%") do set "src_path=%%~dpf"
if exist "%src_path%\Keypirinha" rmdir /Q /S "%src_path%\Keypirinha"
"%SEVENZIP%" x -o"%src_path%" "%src_7z%"
if errorlevel 1 (
    echo Extracting new Keypirinha failed
    pause
    exit /b 1
)
goto after_unpack

:done_winrar
for /f %%f in ("%src_7z%") do set "src_path=%%~dpf"
if exist "%src_path%\Keypirinha" rmdir /Q /S "%src_path%\Keypirinha"
"%WINRAR%" x -ibck "%src_7z%" "%src_path%"
if errorlevel 1 (
    echo Extracting new Keypirinha failed
    pause
    exit /b 1
)
goto after_unpack


:after_unpack
taskkill /IM keypirinha-x64.exe /F
taskkill /IM keypirinha-x86.exe /F
taskkill /IM keypirinha.exe /F

robocopy "%dest_path%" "%temp%\kp_bak" *.* /XD portable /XF portable.ini /MOVE
if errorlevel 4 (
    echo Error removing old installation
    pause
    exit /b 1
)
robocopy "%src_path%\Keypirinha" "%dest_path%" *.* /E /XD portable /XF portable.ini
if errorlevel 4 (
    echo Error copying new installation
    pause
    exit /b 1
)

rmdir /Q /S "%temp%\kp_bak"
del / Q "%src_7z%"
rmdir /Q /S "%src_path%\Keypirinha"

exit /b 0
