:: Prerequisites: Python 3.8 available with "python", "pyrcc5" (installed with PyQt), Nuitka, PyInstaller and Inno Setup 6
set version=5.0

:: compile resources
pyrcc5 "../../src/resources.qrc" -o "../../src/wingman/resources.py"

:: compile application with Nuitka - currently used in hybrid with PyInstaller
del wingman*
python -m nuitka --module ../../src/wingman --include-package=wingman --assume-yes-for-downloads

:: build exe with PyInstaller
rmdir /s /q "dist"
python -m PyInstaller windows.spec -y

:: remove unnecessary files
chdir "dist/Wingman"
rmdir /s /q "PyQt5/Qt5/translations"
rmdir /s /q "PyQt5/Qt5/qml"
del /q Qt5Bluetooth.dll Qt5Location.dll Qt5Nfc.dll Qt5Sensors.dll Qt5Multimedia.dll
del /q Qt5PositioningQuick.dll Qt5DBus.dll Qt5SerialPort.dll Qt5Sql.dll Qt5Test.dll
del /q Qt5XmlPatterns.dll
del /q Qt5Quick3DAssetImport.dll Qt5Quick3DRender.dll Qt5Quick3DRuntimeRender.dll
del /q Qt5Quick3DUtils.dll Qt5QuickControls2.dll Qt5QuickParticles.dll Qt5QuickTemplates.dll
del /q Qt5QuickTest.dll opengl32sw.dll

:: generate portable distributable
chdir ".."
"C:\Program Files\7-Zip\7z.exe" a -tzip -mx=9 -mm=LZMA wingman-%version%-portable.zip Wingman
:: generate installer
chdir ".."
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
