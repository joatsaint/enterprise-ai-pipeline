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
echo Pipeline started -- %DATE% %TIME%   >> "%LOGFILE%"
echo ===================================  >> "%LOGFILE%"

:: ----------------------------------------------------------------
:: STEP 0 -- Health check
:: ----------------------------------------------------------------

echo Running health check...
echo Running health check... >> "%LOGFILE%"
call python health_check.py >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Health check failed -- aborting pipeline
    echo ERROR: Health check failed -- aborting pipeline >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Health check FAILED]
    goto :notify
)
echo Health check passed -- OK
echo Health check passed -- OK >> "%LOGFILE%"
echo.

:: ----------------------------------------------------------------
:: STEP 1 -- Download all groups
:: ----------------------------------------------------------------

echo Running incremental download -- ai-and-claude-code...
echo Running incremental download -- ai-and-claude-code... >> "%LOGFILE%"
call python -m src.main group ai-and-claude-code >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: ai-and-claude-code download failed
    echo ERROR: ai-and-claude-code download failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [ai-and-claude-code FAILED]
) else (
    echo ai-and-claude-code complete -- OK
    echo ai-and-claude-code complete -- OK >> "%LOGFILE%"
)

echo Running incremental download -- career-and-job-search...
echo Running incremental download -- career-and-job-search... >> "%LOGFILE%"
call python -m src.main group career-and-job-search >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: career-and-job-search download failed
    echo ERROR: career-and-job-search download failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [career-and-job-search FAILED]
) else (
    echo career-and-job-search complete -- OK
    echo career-and-job-search complete -- OK >> "%LOGFILE%"
)

echo Running incremental download -- developer-technical...
echo Running incremental download -- developer-technical... >> "%LOGFILE%"
call python -m src.main group developer-technical >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: developer-technical download failed
    echo ERROR: developer-technical download failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [developer-technical FAILED]
) else (
    echo developer-technical complete -- OK
    echo developer-technical complete -- OK >> "%LOGFILE%"
)

echo Running incremental download -- enterprise-strategy...
echo Running incremental download -- enterprise-strategy... >> "%LOGFILE%"
call python -m src.main group enterprise-strategy >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: enterprise-strategy download failed
    echo ERROR: enterprise-strategy download failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [enterprise-strategy FAILED]
) else (
    echo enterprise-strategy complete -- OK
    echo enterprise-strategy complete -- OK >> "%LOGFILE%"
)

:: ----------------------------------------------------------------
:: STEP 2 -- Index
:: ----------------------------------------------------------------

echo Running indexer...
echo Running indexer... >> "%LOGFILE%"
call python -m src.main index >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Index step failed
    echo ERROR: Index step failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Index FAILED]
) else (
    echo Index complete -- OK
    echo Index complete -- OK >> "%LOGFILE%"
)

:: ----------------------------------------------------------------
:: STEP 3 -- Digest
:: ----------------------------------------------------------------

echo Running digest...
echo Running digest... >> "%LOGFILE%"
call python -m src.main digest >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Digest step failed
    echo ERROR: Digest step failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Digest FAILED]
) else (
    echo Digest complete -- OK
    echo Digest complete -- OK >> "%LOGFILE%"
)

:: ----------------------------------------------------------------
:: STEP 4 -- Pain point analysis (all 4 groups)
:: ----------------------------------------------------------------

echo Running pain point analysis -- ai-and-claude-code...
echo Running pain point analysis -- ai-and-claude-code... >> "%LOGFILE%"
call python -m src.main analyze --group ai-and-claude-code >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: ai-and-claude-code analysis failed
    echo ERROR: ai-and-claude-code analysis failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Analyze ai-and-claude-code FAILED]
) else (
    echo ai-and-claude-code analysis complete -- OK
    echo ai-and-claude-code analysis complete -- OK >> "%LOGFILE%"
)

echo Running pain point analysis -- career-and-job-search...
echo Running pain point analysis -- career-and-job-search... >> "%LOGFILE%"
call python -m src.main analyze --group career-and-job-search >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: career-and-job-search analysis failed
    echo ERROR: career-and-job-search analysis failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Analyze career-and-job-search FAILED]
) else (
    echo career-and-job-search analysis complete -- OK
    echo career-and-job-search analysis complete -- OK >> "%LOGFILE%"
)

echo Running pain point analysis -- developer-technical...
echo Running pain point analysis -- developer-technical... >> "%LOGFILE%"
call python -m src.main analyze --group developer-technical >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: developer-technical analysis failed
    echo ERROR: developer-technical analysis failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Analyze developer-technical FAILED]
) else (
    echo developer-technical analysis complete -- OK
    echo developer-technical analysis complete -- OK >> "%LOGFILE%"
)

echo Running pain point analysis -- enterprise-strategy...
echo Running pain point analysis -- enterprise-strategy... >> "%LOGFILE%"
call python -m src.main analyze --group enterprise-strategy >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: enterprise-strategy analysis failed
    echo ERROR: enterprise-strategy analysis failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Analyze enterprise-strategy FAILED]
) else (
    echo enterprise-strategy analysis complete -- OK
    echo enterprise-strategy analysis complete -- OK >> "%LOGFILE%"
)

:: ----------------------------------------------------------------
:: WRAP UP
:: ----------------------------------------------------------------

echo ===================================  >> "%LOGFILE%"
echo Pipeline %STATUS% -- %DATE% %TIME%  >> "%LOGFILE%"
if defined ERRORS echo Errors: %ERRORS%  >> "%LOGFILE%"
echo ===================================  >> "%LOGFILE%"

::  Send email notification
:notify
echo.
echo Sending email notification...
powershell -ExecutionPolicy Bypass -File "%PSSCRIPT%" -Status "%STATUS%" -Errors "%ERRORS%" -LogFile "%LOGFILE%" -Email "%PIPELINE_EMAIL%" -Password "%PIPELINE_PASSWORD%"

echo.
echo Pipeline finished with status: %STATUS%
echo Log file: %LOGFILE%
