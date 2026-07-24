[CmdletBinding()]
param(
    [string]$TaskName = "KNU_ToastNotification",
    [ValidateRange(5, 1440)]
    [int]$IntervalMinutes = 30,
    [string]$ExecutablePath,
    [switch]$SkipInitialize
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($ExecutablePath)) {
    $ExecutablePath = Join-Path $PSScriptRoot "..\dist\KNUToastNotification.exe"
}
$resolvedExecutable = (Resolve-Path -LiteralPath $ExecutablePath).Path
$workingDirectory = Split-Path -Parent $resolvedExecutable
$userId = "$env:USERDOMAIN\$env:USERNAME"

if (-not $SkipInitialize) {
    $initializeProcess = Start-Process `
        -FilePath $resolvedExecutable `
        -ArgumentList "--initialize" `
        -WindowStyle Hidden `
        -Wait `
        -PassThru
    if ($initializeProcess.ExitCode -ne 0) {
        throw "Initialization failed. Check the application log."
    }
}

$action = New-ScheduledTaskAction `
    -Execute $resolvedExecutable `
    -WorkingDirectory $workingDirectory

$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $userId
$scheduledTrigger = New-ScheduledTaskTrigger -Daily -At ((Get-Date).AddMinutes(1))
$repetition = New-CimInstance `
    -ClassName MSFT_TaskRepetitionPattern `
    -Namespace Root/Microsoft/Windows/TaskScheduler `
    -ClientOnly `
    -Property @{
        Interval = "PT${IntervalMinutes}M"
        Duration = "P1D"
        StopAtDurationEnd = $false
    }
$scheduledTrigger.Repetition = $repetition

$principal = New-ScheduledTaskPrincipal `
    -UserId $userId `
    -LogonType Interactive `
    -RunLevel Limited

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -ne $existingTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$legacyTaskName = "KNU_" + [char]0xC54C + [char]0xB9BC
$legacyTask = Get-ScheduledTask -TaskName $legacyTaskName -ErrorAction SilentlyContinue
if ($null -ne $legacyTask) {
    try {
        Unregister-ScheduledTask -TaskName $legacyTaskName -Confirm:$false
    }
    catch {
        Write-Warning (
            "The legacy task could not be removed. " +
            "Run this script once from an elevated PowerShell window to remove it."
        )
    }
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger @($logonTrigger, $scheduledTrigger) `
    -Principal $principal `
    -Settings $settings `
    -Description "Shows Windows notifications for new KNU CSE notices." `
    -Force | Out-Null

Write-Host "Scheduled task registered: $TaskName (at logon and every ${IntervalMinutes} minutes)"
