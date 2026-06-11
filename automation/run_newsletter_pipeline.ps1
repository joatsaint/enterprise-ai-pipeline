# Weekly newsletter curation pipeline — runs the headless Claude pipeline
# (fetch -> curate -> digest -> folder-move) via the Outlook Composio MCP
# connection. See automation/newsletter_pipeline_prompt.md for the full
# step-by-step instructions given to Claude.
#
# Intended for Windows Task Scheduler, same pattern as run_pipeline.bat.

$RepoPath = "C:\Users\joatsaint\Desktop\On Desktop HP-CapCut Network Share\Claude Code My Projects\youtube-downloader"
Set-Location $RepoPath

$LogFile = Join-Path $RepoPath "logs\newsletter_pipeline_run.log"
$PromptFile = Join-Path $RepoPath "automation\newsletter_pipeline_prompt.md"

$allowedTools = @(
    "Read(logs/*)",
    "Read(newsletter_sources.json)",
    "Write(logs/newsletter_fetch_cache.json)",
    "Write(logs/error_log.json)",
    "Bash(python -m src.main curate-newsletters*)",
    "mcp__outlook-composio__COMPOSIO_GET_TOOL_SCHEMAS",
    "mcp__outlook-composio__COMPOSIO_MULTI_EXECUTE_TOOL",
    "mcp__outlook-composio__COMPOSIO_REMOTE_BASH_TOOL"
) -join ","

"=== Newsletter pipeline started -- $(Get-Date) ===" | Out-File -Append -FilePath $LogFile -Encoding utf8

try {
    $prompt = Get-Content -Raw -Encoding utf8 $PromptFile
    $prompt | claude -p --allowedTools $allowedTools --output-format text *>> $LogFile
    "=== Newsletter pipeline finished -- $(Get-Date) ===" | Out-File -Append -FilePath $LogFile -Encoding utf8
} catch {
    "=== Newsletter pipeline ERROR -- $(Get-Date): $_ ===" | Out-File -Append -FilePath $LogFile -Encoding utf8
}
