@echo off
set "REPOPATH=C:\Users\joatsaint\Desktop\On Desktop HP-CapCut Network Share\Claude Code My Projects\youtube-downloader"
set "LOGFILE=%REPOPATH%\logs\video_development_weekly.log"
set STATUS=SUCCESS
set ERRORS=

cd /d "%REPOPATH%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Could not change to repo directory
    exit /b 1
)

echo ===================================  >> "%LOGFILE%"
echo video-development weekly run -- %DATE% %TIME%  >> "%LOGFILE%"
echo ===================================  >> "%LOGFILE%"

:: Deliberately separate from run_pipeline.bat: video-development is a
:: showrunner/TV-format study group (Daryn Strauss), NOT an ICP research
:: group. It must stay out of pain-point analysis and the main daily
:: digest -- see channels.json display_names note and
:: memory/project_daryn_strauss_showrunner_research.md.

echo Running incremental download -- video-development... >> "%LOGFILE%"
call python -m src.main group video-development >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: video-development download failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [video-development download FAILED]
) else (
    echo video-development download complete -- OK >> "%LOGFILE%"
)

echo Running indexer... >> "%LOGFILE%"
call python -m src.main index >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Index step failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [Index FAILED]
) else (
    echo Index complete -- OK >> "%LOGFILE%"
)

echo Running digest -- video-development (since last run)... >> "%LOGFILE%"
call python -m src.main digest --group video-development --scheduled >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: video-development digest failed >> "%LOGFILE%"
    set STATUS=FAILED
    set ERRORS=%ERRORS% [video-development digest FAILED]
) else (
    echo video-development digest complete -- OK >> "%LOGFILE%"
)

echo ===================================  >> "%LOGFILE%"
echo video-development weekly run %STATUS% -- %DATE% %TIME%  >> "%LOGFILE%"
if defined ERRORS echo Errors: %ERRORS%  >> "%LOGFILE%"
echo ===================================  >> "%LOGFILE%"

echo.
echo video-development weekly run finished with status: %STATUS%
echo Log file: %LOGFILE%
