# check-claude-code-updates.ps1
#
# Flags when a new Claude Code release has shipped since the last time this
# checked, so new capabilities (e.g. background sub-agents auto-committing/
# pushing/opening draft PRs, shipped v2.1.198) don't sit unused for weeks
# just because nobody happened to notice the changelog. Randy's own trigger:
# noticed a real behavior improvement, wanted a standing check rather than
# relying on stumbling across a YouTube video about it.
#
# Rate-limited to once per 24 hours (checking every session would be noisy
# and slow) via a local cache file. Read-only against the project itself --
# only ever writes its own cache file, never touches any tracked file.
# Network/gh-CLI failures degrade silently to no output, never blocking
# session start.

$cachePath = Join-Path $PSScriptRoot ".claude_code_version_cache.json"
$now = Get-Date

$cache = $null
if (Test-Path $cachePath) {
    try {
        $cache = Get-Content $cachePath -Raw | ConvertFrom-Json
    } catch {
        $cache = $null
    }
}

if ($cache -and $cache.lastChecked) {
    $lastChecked = [datetime]$cache.lastChecked
    if (($now - $lastChecked).TotalHours -lt 24) {
        # Checked recently -- stay silent, don't nag every session.
        exit 0
    }
}

$latestVersion = $null
try {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($gh) {
        $release = gh api repos/anthropics/claude-code/releases/latest 2>$null | ConvertFrom-Json
        if ($release -and $release.tag_name) {
            $latestVersion = $release.tag_name
        }
    }
} catch {
    $latestVersion = $null
}

if (-not $latestVersion) {
    # No gh CLI, no network, or API failure -- fail silent, don't block.
    exit 0
}

$previousVersion = $null
if ($cache -and $cache.lastSeenVersion) {
    $previousVersion = $cache.lastSeenVersion
}

$newCache = @{
    lastChecked     = $now.ToString("o")
    lastSeenVersion = $latestVersion
}
$newCache | ConvertTo-Json | Set-Content -Path $cachePath -Encoding utf8

if ($previousVersion -and ($previousVersion -ne $latestVersion)) {
    $msg = "Claude Code has a new release since last check: $previousVersion -> $latestVersion. " +
           "Worth a quick look at https://github.com/anthropics/claude-code/releases/tag/$latestVersion " +
           "(or `claude update`) to see if anything changes how this project's workflows should run -- " +
           "e.g. background sub-agents auto-committing/pushing/opening draft PRs (shipped v2.1.198) is " +
           "exactly the kind of capability worth knowing about before manually working around its absence."
    ConvertTo-Json -Compress @{
        hookSpecificOutput = @{
            hookEventName    = "SessionStart"
            additionalContext = $msg
        }
    }
}
# First run (no previous cached version) or no change -- stay silent.
