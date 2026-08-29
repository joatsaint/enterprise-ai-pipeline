@echo off
REM ============================================================
REM  Weekly Content Loop — the "research mastermind checkup".
REM  Runs: live source scan (Reddit RSS, Spiceworks, RSS blogs, KB)
REM  -> relevance scoring -> draft -> STOPS at the review gate.
REM  Does NOT publish. Produces drafts in content-engine/pending/
REM  for Randy to review. Run by Task Scheduler "Weekly Content Loop".
REM ============================================================
cd /d "%~dp0"
C:\Python314\python.exe -m src.main loop >> "logs\loop_run.log" 2>&1
exit /b %ERRORLEVEL%
