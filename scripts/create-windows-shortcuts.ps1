[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$LauncherPath,

    [Parameter(Mandatory = $true)]
    [string]$WorkingDirectory,

    [string]$ShortcutName = 'Task Terminal',
    [string]$Description  = 'Keyboard-friendly terminal task manager'
)

$ErrorActionPreference = 'Stop'

$LauncherPath     = $LauncherPath.Trim().TrimEnd('"')
$WorkingDirectory = [System.IO.Path]::GetFullPath($WorkingDirectory.Trim().TrimEnd('"'))

if (-not (Test-Path -LiteralPath $LauncherPath)) {
    Write-Error "Launcher not found: $LauncherPath"
    exit 1
}
if (-not (Test-Path -LiteralPath $WorkingDirectory)) {
    Write-Error "Working directory not found: $WorkingDirectory"
    exit 1
}

function New-AppShortcut {
    param(
        [string]$Path,
        [string]$Target,
        [string]$WorkDir,
        [string]$Desc
    )
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut($Path)
    $lnk.TargetPath       = $Target
    $lnk.WorkingDirectory = $WorkDir
    $lnk.Description      = $Desc
    $lnk.WindowStyle      = 1
    $lnk.Save()
}

$startMenuDir = Join-Path ([Environment]::GetFolderPath('Programs')) ''
$desktopDir   = [Environment]::GetFolderPath('Desktop')

$startLnk   = Join-Path $startMenuDir "$ShortcutName.lnk"
$desktopLnk = Join-Path $desktopDir   "$ShortcutName.lnk"

New-AppShortcut -Path $startLnk   -Target $LauncherPath -WorkDir $WorkingDirectory -Desc $Description
New-AppShortcut -Path $desktopLnk -Target $LauncherPath -WorkDir $WorkingDirectory -Desc $Description

Write-Host "Created Start Menu shortcut: $startLnk"
Write-Host "Created Desktop shortcut:    $desktopLnk"
exit 0
