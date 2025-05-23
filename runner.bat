@ echo-off

cd /d "%~dp0"
start cmd /c "call env\Scripts\activate && python App.py"