;--------------------------------
;Include Modern UI

  !include "MUI.nsh"

;--------------------------------
;General

  ;Name and file
  Name "PyAcqua"
  OutFile "PyAcquaInstaller.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\PyAcqua"
 
  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\PyAcqua" ""

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "COPYING"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
 
  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "-PyAcqua Core" SecDummy

	SetOutPath "$INSTDIR"
	File /r "dist\*.*"
	;File "launcher-win32\pyacqua.exe" ;launcher
	File "win32-merger\pyacqua.exe"
	
	;Store installation folder
	WriteRegStr HKCU "Software\PyAcqua" "" $INSTDIR

	;Create uninstaller
	WriteUninstaller "$INSTDIR\Uninstall.exe"


	CreateShortCut "$INSTDIR\PyAcqua.lnk" "$INSTDIR\pyacqua.exe"

	SetOutPath "$SMPROGRAMS\PyAcqua\"
	CopyFiles "$INSTDIR\PyAcqua.lnk" "$SMPROGRAMS\PyAcqua\"
	CopyFiles "$INSTDIR\PyAcqua.lnk" "$DESKTOP\"
	CreateShortCut "$SMPROGRAMS\PyAcqua\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

SectionEnd

Section "GTK+ Files" SecDummy2

  SetOutPath "$INSTDIR\"
  File "C:\GTK\bin\*.dll"

  SetOutPath "$INSTDIR\etc\fonts\"
  File "C:\GTK\etc\fonts\*.*"

  SetOutPath "$INSTDIR\etc\gtk-2.0\"
  File "C:\GTK\etc\gtk-2.0\*.*"

  SetOutPath "$INSTDIR\etc\pango\"
  File "C:\GTK\etc\pango\*.*"

  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\loaders\"
  File "C:\GTK\lib\gtk-2.0\2.10.0\loaders\*.*"

  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\engines\"
  File "C:\GTK\lib\gtk-2.0\2.10.0\engines\*.*"

  SetOutPath "$INSTDIR\lib\gtk-2.0\2.10.0\immodules\"
  File "C:\GTK\lib\gtk-2.0\2.10.0\immodules\*.*"

  SetOutPath "$INSTDIR\lib\pango\1.6.0\modules\"
  File "C:\GTK\lib\pango\1.6.0\modules\*.*"

  SetOutPath "$INSTDIR\share\themes\Default\gtk-2.0-key\"
  File "C:\GTK\share\themes\Default\gtk-2.0-key\*.*"

  SetOutPath "$INSTDIR\share\themes\MS-Windows\gtk-2.0\"
  File "C:\GTK\share\themes\MS-Windows\gtk-2.0\*.*"

SectionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecDummy ${LANG_ENGLISH} "Main Package. You need this to run pyacqua."
  LangString DESC_SecDummy2 ${LANG_ENGLISH} "GTK+ Package. To be installed if you dont have pre installed GTK+"

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy} $(DESC_SecDummy)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDummy2} $(DESC_SecDummy2)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall" 

  Delete "$INSTDIR\*.*"

  Delete "$DESKTOP\PyAcqua.lnk"
  Delete "$SMPROGRAMS\PyAcqua\PyAcqua.lnk"
  Delete "$SMPROGRAMS\PyAcqua\Uninstall.lnk"

  RMDir /r "$SMPROGRAMS\PyAcqua\"

  RMDir /r "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\PyAcqua"

SectionEnd 