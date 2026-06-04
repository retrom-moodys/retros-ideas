$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$outZip = Join-Path $root "metadata_processor.zip"

if (Test-Path $outZip) { Remove-Item $outZip }

Compress-Archive -Path (Join-Path $root "metadata_processor.py") -DestinationPath $outZip

Write-Host "Created: $outZip"
