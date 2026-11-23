# Install one or more skills from the Claude Skills Library into ~/.claude/skills/ (Windows).
#
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 gauntlet-loop fact-check   # from a cloned copy
#   powershell -ExecutionPolicy Bypass -File .\install.ps1 -List                      # show available skills
#   & ([scriptblock]::Create((irm https://raw.githubusercontent.com/joshuasun26/claude-skills-library/main/install.ps1))) gauntlet-loop
#
# It only copies skill folders. It never edits settings.json, hooks, or anything else.
# An existing skill with the same name is moved to ~/.claude/skills-backups/<name>-<timestamp> first,
# outside the skills folder so Claude does not load two copies.
param(
  [switch]$List,
  [Parameter(ValueFromRemainingArguments = $true)][string[]]$Names
)
$ErrorActionPreference = 'Stop'
$Repo = 'joshuasun26/claude-skills-library'
$Branch = 'main'
$Backup = Join-Path $HOME '.claude\skills-backups'
$Dest = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $HOME '.claude\skills' }

if (-not $List -and (-not $Names -or $Names.Count -eq 0)) {
  Write-Host 'Usage: install.ps1 <skill-name> [more-skill-names]   or   install.ps1 -List'
  return
}

$Src = $null
$Tmp = $null
$Installed = 0; $Failed = 0
try {
  if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot 'skills'))) {
    $Src = Join-Path $PSScriptRoot 'skills'
  } else {
    $Tmp = Join-Path ([IO.Path]::GetTempPath()) ("skills-library-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Tmp | Out-Null
    $Zip = Join-Path $Tmp 'repo.zip'
    Write-Host "Downloading $Repo ($Branch)..."
    Invoke-WebRequest -UseBasicParsing -Uri "https://codeload.github.com/$Repo/zip/refs/heads/$Branch" -OutFile $Zip
    Expand-Archive -Path $Zip -DestinationPath $Tmp
    $Src = (Get-ChildItem -Path $Tmp -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'skills') } | Select-Object -First 1).FullName
    $Src = Join-Path $Src 'skills'
  }

  if ($List) { Get-ChildItem -Path $Src -Directory | ForEach-Object { $_.Name }; return }

  New-Item -ItemType Directory -Force -Path $Dest | Out-Null
  $Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
  $Pair = @{ 'session-refresh' = 'session-handoff-60'; 'session-handoff-60' = 'session-refresh' }
  $Unique = @($Names | Select-Object -Unique)
  foreach ($Name in $Unique) {
    if (-not $Name -or $Name -match '[\/]' -or $Name.StartsWith('.')) { Write-Host "Skipping invalid name: $Name"; $Failed++; continue }
    $From = Join-Path $Src $Name
    if (-not (Test-Path (Join-Path $From 'SKILL.md'))) { Write-Host "Not found: $Name  (run with -List to see names)"; $Failed++; continue }
    $Other = $Pair[$Name]
    if ($Other -and ((Test-Path (Join-Path $Dest $Other)) -or ($Unique -contains $Other))) {
      Write-Host "Note: $Name and $Other are pick-one. Use only one; remove the other from $Dest before finishing setup."
    }
    $To = Join-Path $Dest $Name
    if (Test-Path $To) {
      New-Item -ItemType Directory -Force -Path $Backup | Out-Null
      $Old = Join-Path $Backup "$Name-$Stamp"
      Move-Item -Path $To -Destination $Old
      Write-Host "Kept your old copy at $Old"
    }
    Copy-Item -Path $From -Destination $To -Recurse
    Write-Host "Installed $Name -> $To"
    $Installed++
    if ($Other) {
      $Extra = ''
      if (Test-Path (Join-Path $To 'INSTALL-PROMPT.md')) { $Extra = " and $(Join-Path $To 'INSTALL-PROMPT.md')" }
      Write-Host "  Next: open Claude Code and say: Read $(Join-Path $To 'SKILL.md')$Extra and finish the install. Back up my settings and show me the diff first."
    }
  }
  if ($Installed -gt 0) { Write-Host "Done: $Installed installed. Start a new Claude Code session to load new skills." }
  else { Write-Host 'Nothing was installed.' }
} finally {
  if ($Tmp -and (Test-Path $Tmp)) { Remove-Item -LiteralPath $Tmp -Recurse -Force -ErrorAction SilentlyContinue }
}
if ($Failed -gt 0 -or ($Installed -eq 0 -and -not $List)) { exit 1 }
