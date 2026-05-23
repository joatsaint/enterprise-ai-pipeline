@echo off
set "REPOPATH=C:\Users\joatsaint\Desktop\On Desktop HP-CapCut Network Share\Claude Code My Projects\youtube-downloader"
set "LOGFILE=%REPOPATH%\logs\pipeline_run.log"
set "SECRETSFILE=%REPOPATH%\pipeline_secrets.env"
set "PSSCRIPT=%REPOPATH%\send_notification.ps1"
set STATUS=SUCCESS
set ERRORS=

:: Load secrets from pipeline_secrets.env
for /f "usebackq tokens=1,2 delims==" %%a in ("%SECRETSFILE%") do set %%a=%%b

echo Secrets loaded. Path: %REPOPATH%
echo.

cd /d "%REPOPATH%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Could not change to repo directory
    pause
    exit /b 1
)

echo Changed to repo directory OK
echo.

echo ===================================  >> "%LOGFILE%"
echo Pipeline started — %DATE% %TIME%    >> "%LOGFILE%"
echo ===================================  >> "%LOGFILE%"

:: STEP 1 — Incremental Download
echo Running incremental download...
echo Running incremental download...      >> "%LOGFILE%"
call python main.py download --incremental >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Download step failed
    echo ERROR: Download step failed       >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Download FAILED]
) else (
    echo Download complete — OK
    echo Download complete — OK            >> "%LOGFILE%"
)

:: STEP 2 — Indexer
echo Running indexer...
echo Running indexer...                   >> "%LOGFILE%"
call python main.py index >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Index step failed
    echo ERROR: Index step failed          >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Index FAILED]
) else (
    echo Index complete — OK
    echo Index complete — OK               >> "%LOGFILE%"
)

:: STEP 3 — Digest
echo Running digest...
echo Running digest...                    >> "%LOGFILE%"
call python main.py digest >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Digest step failed
    echo ERROR: Digest step failed         >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Digest FAILED]
) else (
    echo Digest complete — OK
    echo Digest complete — OK              >> "%LOGFILE%"
)

echo ===================================  >> "%LOGFILE%"
echo Pipeline %STATUS% — %DATE% %TIME%   >> "%LOGFILE%"
if defined ERRORS echo Errors: %ERRORS%  >> "%LOGFILE%"
echo ===================================  >> "%LOGFILE%"

:: Call PowerShell script for email
echo Sending email notification...
powershell -ExecutionPolicy Bypass -File "%PSSCRIPT%" -Status "%STATUS%" -Errors "%ERRORS%" -LogFile "%LOGFILE%" -Email "%PIPELINE_EMAIL%" -Password "%PIPELINE_PASSWORD%"

echo.
echo Pipeline finished with status: %STATUS%
echo Log file: %LOGFILE%
pause
