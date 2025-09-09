# Quick wheelhouse upload script
# Uses the Windows-compatible utility

Write-Host "NextCloud Wheelhouse Upload" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""

python scripts\nextcloud_upload_windows.py --wheelhouse

Write-Host ""
Write-Host "Upload complete. Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")