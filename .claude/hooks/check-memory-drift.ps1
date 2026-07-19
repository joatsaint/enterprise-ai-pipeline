# check-memory-drift.ps1
#
# Flags possible drift between what's committed in git and what the
# memory status files (HOT_STATE.md, SESSION_LOG.md) claim -- never edits
# either side. Real trigger: those files are gitignored on purpose (see
# CLAUDE.md), so there's no way to keep them "in sync" with git
# automatically without risking overwriting carefully-reasoned narrative
# content. This script's only job is to surface the raw facts -- how many
# commits landed in each repo after a memory file was last touched -- and
# let the reader (Randy or Claude at session start) judge whether that
# gap is real neglect or normal same-session lag.
#
# Never auto-edits HOT_STATE.md, SESSION_LOG.md, or any git-tracked file.
# Read-only in every direction.

$repoRoot = "C:\Users\joatsaint\Desktop\On Desktop HP-CapCut Network Share\Claude Code My Projects\youtube-downloader"

$repos = @(
    @{ Name = "youtube-downloader"; Path = $repoRoot }
    @{ Name = "swarmops-core"; Path = Join-Path $repoRoot "project-monte-swarmops-core" }
    @{ Name = "voice-line"; Path = Join-Path $repoRoot "Jarvis Project\voice-line" }
)

$memoryFiles = @(
    @{ Name = "HOT_STATE.md"; Path = Join-Path $repoRoot "memory\HOT_STATE.md" }
    @{ Name = "SESSION_LOG.md"; Path = Join-Path $repoRoot "memory\SESSION_LOG.md" }
)

$lines = @()

foreach ($repo in $repos) {
    if (-not (Test-Path (Join-Path $repo.Path ".git"))) {
        continue
    }

    Push-Location $repo.Path
    $latest = git log -1 --format='%h %ci %s' 2>$null
    Pop-Location

    if (-not $latest) {
        continue
    }

    $lines += "$($repo.Name) latest commit: $latest"

    foreach ($mem in $memoryFiles) {
        if (-not (Test-Path $mem.Path)) {
            continue
        }
        $memTime = (Get-Item $mem.Path).LastWriteTime
        $memTimeIso = $memTime.ToString("yyyy-MM-dd HH:mm:ss")

        Push-Location $repo.Path
        $commitsSince = git log --since="$memTimeIso" --format='%h %ci %s' 2>$null
        Pop-Location

        $count = 0
        if ($commitsSince) {
            $count = ($commitsSince | Measure-Object -Line).Lines
        }

        if ($count -gt 0) {
            $lines += "  FLAG: $count commit(s) in $($repo.Name) landed after $($mem.Name) was last edited ($memTimeIso):"
            foreach ($c in $commitsSince) {
                $lines += "    - $c"
            }
        }
    }
}

if ($lines.Count -eq 0) {
    $msg = "No repos with git history found -- nothing to check."
} else {
    $footer = "This is a raw flag, not a verdict. A commit landing shortly after a memory-file edit within the same working session is often normal turn-sequencing lag, not neglect -- judge by reading the actual commit messages against the memory file's narrative content, not by count alone."
    $msg = ($lines -join "`n") + "`n`n$footer"
}

ConvertTo-Json -Compress @{
    hookSpecificOutput = @{
        hookEventName    = "SessionStart"
        additionalContext = $msg
    }
}
