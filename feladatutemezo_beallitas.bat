@echo off
:: Civil Ház – Napi hírfrissítő beállítása Windows Feladatütemezőbe
:: Futtassa rendszergazdaként!
:: --------------------------------------------------------

set SCRIPT="J:\Saját meghajtó\Claude Workspace\CODE\WEB PAGES\civilhazveszprem\update_hirek.py"
set TASK_NAME="CivilHaz_Hirek_Frissites"
set PYTHON_EXE="py"

echo.
echo =====================================================
echo  Civil Ház – Napi hírfrissítő telepítése
echo  Ütemezés: Minden nap 07:00
echo =====================================================
echo.

:: Korábbi feladat törlése (ha van)
schtasks /Delete /TN %TASK_NAME% /F >nul 2>&1

:: Feladat létrehozása: naponta 07:00-kor
schtasks /Create ^
  /TN %TASK_NAME% ^
  /TR "%PYTHON_EXE% -3 %SCRIPT%" ^
  /SC DAILY ^
  /ST 07:00 ^
  /RU "%USERNAME%" ^
  /RL HIGHEST ^
  /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo  [OK] Feladat sikeresen létrehozva!
    echo.
    echo  Neve:       %TASK_NAME%
    echo  Ütemezés:   Minden nap 07:00
    echo  Szkript:    %SCRIPT%
    echo.
    echo  A feladat a Windows Feladatütemezőben megtekinthető:
    echo  Start → Feladatütemező → Feladatütemező könyvtár
    echo.
    echo  FONTOS: Szükséges az Anthropic API kulcs beírása az update_hirek.py fájlba!
    echo  Sor:  API_KEY = "IDE_ÍRJA_BE_AZ_ANTHROPIC_API_KULCSÁT"
    echo.
) else (
    echo.
    echo  [HIBA] A feladat létrehozása sikertelen.
    echo  Futtassa a .bat fájlt rendszergazdaként!
    echo.
)

pause
