import os
import winreg

# Resolve o .exe correto dinamicamente: dist/WeatherWallpaper.exe ao lado do repo.
# (Antes apontava para E:\... + layout onedir antigo dist\WeatherWallpaper\*.exe)
ROOT = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(ROOT, "dist", "WeatherWallpaper.exe")
cmd  = f'"{path}" --minimized'

k = winreg.OpenKey(
    winreg.HKEY_CURRENT_USER,
    r"Software\Microsoft\Windows\CurrentVersion\Run",
    0, winreg.KEY_SET_VALUE
)
winreg.SetValueEx(k, "WeatherWallpaper", 0, winreg.REG_SZ, cmd)
winreg.CloseKey(k)
print(f"Registro atualizado:\n{cmd}")