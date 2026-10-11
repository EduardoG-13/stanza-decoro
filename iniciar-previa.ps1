param([int]$Port = 8935)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$siteProjectPath = $PSScriptRoot
Set-Location -LiteralPath $siteProjectPath
$env:PYTHONIOENCODING = 'utf-8'
python scripts/build.py
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível preparar a prévia.' }
Write-Host "Prévia da Stanza: http://127.0.0.1:$Port/index.html"
Write-Host 'Mantenha esta janela aberta. Use Ctrl+C para encerrar a prévia.'
if (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue) {
    throw "A porta $Port já está em uso. Tente iniciar com -Port 8936."
}
$sitePythonExecutable = (Get-Command python -ErrorAction Stop).Source
$siteServerProcess = Start-Process -FilePath $sitePythonExecutable -ArgumentList @('-m','http.server',$Port.ToString(),'--bind','127.0.0.1','--directory','dist') -WorkingDirectory $siteProjectPath -WindowStyle Hidden -PassThru
try {
    $siteReady = $false
    for ($siteAttempt = 0; $siteAttempt -lt 20; $siteAttempt++) {
        try {
            $siteResponse = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/assets/build-info.json" -UseBasicParsing -TimeoutSec 2
            if ($siteResponse.StatusCode -eq 200) { $siteReady = $true; break }
        } catch { Start-Sleep -Milliseconds 250 }
    }
    if (-not $siteReady) { throw 'A prévia não conseguiu iniciar.' }
    Start-Process "http://127.0.0.1:$Port/index.html"
    Wait-Process -Id $siteServerProcess.Id
} finally {
    if (-not $siteServerProcess.HasExited) { Stop-Process -Id $siteServerProcess.Id -ErrorAction SilentlyContinue }
}
