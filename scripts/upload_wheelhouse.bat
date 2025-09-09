@echo off
REM Quick wheelhouse upload script
REM Uses the Windows-compatible utility

echo NextCloud Wheelhouse Upload
echo =============================

python scripts\nextcloud_upload_windows.py --wheelhouse

echo.
echo Upload complete. Press any key to exit...
pause >nul