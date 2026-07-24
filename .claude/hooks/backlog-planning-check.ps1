# backlog-planning-check.ps1
#
# UserPromptSubmit hook -- the "planning intent detected" trigger from
# PHASE_2_DESIGN.md Section 2. New hook type for this project; no
# UserPromptSubmit entry existed in settings.local.json before this file.
#
# Behavior:
#   1. Read the incoming prompt text from stdin (Claude Code delivers
#      UserPromptSubmit input as JSON on stdin; the exact field name is
#      inferred from this project's existing hook conventions and has NOT
#      yet been confirmed by a live fire -- see PHASE_2_DESIGN.md Section 5's
#      flagged open item. This script therefore tries the most likely field
#      names and falls back to the raw stdin text if none match, so a wrong
#      guess degrades to "classify the raw JSON blob" (safe: raw JSON containing
#      planning keywords still classifies as planning/uncertain) rather than
#      silently doing nothing.
#   2. Pipe that text into `python -m src.backlog.cli check-intent
#      youtube-downloader`, which does the real classification + verification
#      + logging (src/backlog/cli.py, src/backlog/intent.py).
#   3. On PASS with no output: emit nothing -- quiet by design (Section 4).
#   4. On any output from the Python side (a verification block, pass or
#      fail): inject it via additionalContext so it's visible in context
#      before Claude answers.
#   5. On ANY error in this script itself (Python missing, working directory
#      wrong, etc.): DO NOT fail silently -- emit a visible warning block
#      instead of empty output, per Section 3's hard requirement that a
#      broken check must never look identical to "nothing needed checking."
#
# Every invocation is also independently logged by the Python side to
# logs/backlog_hook_runs.jsonl regardless of what this wrapper does --
# that log is the audit trail Randy can check directly if this script's own
# behavior is ever in doubt.

$repoRoot = "C:\Users\joatsaint\Desktop\On Desktop HP-CapCut Network Share\Claude Code My Projects\youtube-downloader"

try {
    $stdinRaw = [Console]::In.ReadToEnd()

    $promptText = $stdinRaw
    if ($stdinRaw) {
        try {
            $parsed = $stdinRaw | ConvertFrom-Json -ErrorAction Stop
            if ($parsed.prompt) { $promptText = $parsed.prompt }
            elseif ($parsed.user_prompt) { $promptText = $parsed.user_prompt }
            elseif ($parsed.message) { $promptText = $parsed.message }
            # else: no known field matched -- fall back to the raw JSON text
            # already assigned above, rather than silently using an empty string.
        } catch {
            # Not JSON -- treat stdin as the raw prompt text directly.
        }
    }

    Push-Location $repoRoot
    $output = $promptText | python -m src.backlog.cli check-intent youtube-downloader 2>&1
    $exitCode = $LASTEXITCODE
    Pop-Location

    if ($output) {
        $msg = ($output -join "`n")
        ConvertTo-Json -Compress @{
            hookSpecificOutput = @{
                hookEventName     = "UserPromptSubmit"
                additionalContext = $msg
            }
        }
    }
    # No output at all (non_planning classification, nothing printed) --
    # intentionally silent, matching the "quiet on pass" visibility rule.
} catch {
    $errMsg = "Planning verification hook encountered an error: $_"
    ConvertTo-Json -Compress @{
        systemMessage      = "WARNING: $errMsg"
        hookSpecificOutput = @{
            hookEventName     = "UserPromptSubmit"
            additionalContext = $errMsg
        }
    }
}
