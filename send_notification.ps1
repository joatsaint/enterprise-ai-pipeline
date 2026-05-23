param(
    [string]$Status,
    [string]$Errors,
    [string]$LogFile,
    [string]$Email,
    [string]$Password
)

$Date = Get-Date -Format 'yyyy-MM-dd'
$DateTime = Get-Date -Format 'yyyy-MM-dd HH:mm'
$Subject = "YouTube Pipeline $Status - $Date"

try {
    $LogContent = Get-Content $LogFile -Tail 40 -Raw
} catch {
    $LogContent = "Could not read log file: $LogFile"
}

if ($Status -eq 'FAILED') {
    $Body = "PIPELINE FAILED on $DateTime`r`nFailed steps: $Errors`r`n`r`nCheck the log below for details.`r`n`r`n$LogContent"
} else {
    $Body = "Pipeline completed successfully on $DateTime`r`nAll steps passed: Download, Index, Digest.`r`n`r`nLast 40 lines of log:`r`n`r`n$LogContent"
}

try {
    $SecurePassword = ConvertTo-SecureString $Password -AsPlainText -Force
    $Credential = New-Object System.Management.Automation.PSCredential($Email, $SecurePassword)

    Send-MailMessage `
        -To $Email `
        -From $Email `
        -Subject $Subject `
        -Body $Body `
        -SmtpServer "smtp.gmail.com" `
        -Port 587 `
        -UseSsl `
        -Credential $Credential

    Write-Host "Email sent successfully to $Email"
} catch {
    Write-Host "ERROR sending email: $($_.Exception.Message)"
}
