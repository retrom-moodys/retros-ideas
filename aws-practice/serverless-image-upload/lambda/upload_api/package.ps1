$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$outZip = Join-Path $root "upload_api.zip"

if (Test-Path $outZip) { Remove-Item $outZip }

Compress-Archive -Path (Join-Path $root "upload_api.py") -DestinationPath $outZip

Write-Host "Created: $outZip"
Write-Host ""
Write-Host "Upload to Lambda (replace FUNCTION_NAME):"
Write-Host "  aws lambda update-function-code --function-name FUNCTION_NAME --zip-file fileb://$outZip"
Write-Host ""
Write-Host "Environment variables (Lambda console → Configuration → Environment variables):"
Get-Content (Join-Path $root "env.example") | Where-Object { $_ -and $_ -notmatch '^#' }
