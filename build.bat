@echo off
echo === Limpiando compilaciones anteriores ===
rmdir /S /Q build dist 2>nul
del /Q main.spec 2>nul
echo === Compilando RLC Simulador ===
pyinstaller --onefile --windowed ^
  --name "SimuladorRLC" ^
  --icon=icon.ico ^
  --hidden-import=pyqtgraph ^
  --hidden-import=pyqtgraph.graphicsItems ^
  --hidden-import=pyqtgraph.widgets ^
  main.py
echo === Listo: dist\SimuladorRLC.exe ===
pause
