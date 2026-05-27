import winreg

path = r"E:\PROJETOS\Weather-Wallpaper\dist\WeatherWallpaper\WeatherWallpaper.exe"
cmd  = f'"{path}" --minimized'

k = winreg.OpenKey(
    winreg.HKEY_CURRENT_USER,
    r"Software\Microsoft\Windows\CurrentVersion\Run",
    0, winreg.KEY_SET_VALUE
)
winreg.SetValueEx(k, "WeatherWallpaper", 0, winreg.REG_SZ, cmd)
winreg.CloseKey(k)
print(f"Registro atualizado:\n{cmd}")