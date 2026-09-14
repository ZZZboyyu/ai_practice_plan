chcp 65001 | Out-Null
$utf8 = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding = $utf8
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
Write-Host "PowerShell is using UTF-8."
