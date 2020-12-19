:: Prerequisites: Python >=3.7 available with "py", "pyrcc5" (installed with PyQt), Nuitka, PyInstaller and Inno Setup 6

:: compile resources
pyrcc5 "../../src/resources.qrc" -o "../../src/wingman/resources.py"

:: compile application with Nuitka - currently used in hybrid with PyInstaller
py -m nuitka --module ../../src/wingman --include-package=wingman

:: build exe with PyInstaller
py -m PyInstaller windows.spec -y

:: remove unnecessary files
chdir "./dist/Wingman/"
rmdir /s /q "PyQt5/Qt/translations"
rmdir /s /q "PyQt5/Qt/qml"
del /q Qt5Bluetooth.dll Qt5Location.dll Qt5Nfc.dll Qt5Sensors.dll Qt5Multimedia.dll
del /q Qt5PositioningQuick.dll Qt5DBus.dll Qt5SerialPort.dll Qt5Sql.dll Qt5Test.dll
del /q Qt5XmlPatterns.dll
del /q Qt5Quick3DAssetImport.dll Qt5Quick3DRender.dll Qt5Quick3DRuntimeRender.dll
del /q Qt5Quick3DUtils.dll Qt5QuickControls2.dll Qt5QuickParticles.dll Qt5QuickTemplates.dll
del /q Qt5QuickTest.dll opengl32sw.dll

explorer .

:: generate installer
chdir "./../../"
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
