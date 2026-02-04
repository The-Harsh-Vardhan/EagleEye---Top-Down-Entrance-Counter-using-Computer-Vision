@echo off
title EagleEye - People Counting System
echo ========================================
echo    EagleEye - Starting System
echo ========================================
echo.

cd /d "%~dp0"

:: Start dashboard in background
echo Starting Dashboard...
start "EagleEye Dashboard" cmd /c "python -m streamlit run dashboard.py"

:: Wait for dashboard to start
timeout /t 3 /nobreak >nul

:: Open dashboard in browser
start http://localhost:8501

:: Start main application with test video
echo.
echo Starting People Counter (test1.mp4 + Motion Detection)...
echo Press 'q' in the video window to quit
echo.
python main.py --source Dataset/test1.mp4 --motion --rotate 90

echo.
echo EagleEye stopped.
pause
