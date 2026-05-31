@echo off
cd /d "%~dp0"
echo Installing dependencies...
python -m pip install -r requirements.txt
echo.
echo Starting FoodHub with ASGI (WebSocket) support...
echo Open http://127.0.0.1:8000/
echo.
python -m daphne -b 127.0.0.1 -p 8000 food_ordering_system.asgi:application
pause
