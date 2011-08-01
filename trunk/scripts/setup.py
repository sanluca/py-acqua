from distutils.core import setup 
import glob
import py2exe 
 
setup( 
    name = 'PyAcqua', 
    description = 'Programma per la gestione degli acquari.', 
    version = '0.9', 
 
    windows = [ 
                  { 
                      'script': 'acqua.py', 
                      'icon_resources': [(1, "pyacqua.ico")], 
                  } 
              ], 
 
    options = { 
                  'py2exe': { 
                      'packages': 'encodings, pychart', 
                      'includes': 'dircache, cairo, pango, pangocairo, atk, gobject, pysqlite2', 
					  "dll_excludes": [
						"iconv.dll","intl.dll","libatk-1.0-0.dll",
						"libgdk_pixbuf-2.0-0.dll", "libgdk–win32-2.0-0.dll",
						"libglib-2.0-0.dll", "libgmodule-2.0-0.dll",
						"libgobject-2.0-0.dll", "libgthread-2.0-0.dll",
						"libgtk–win32-2.0-0.dll", "libpango-1.0-0.dll",
						"libpangowin32-1.0-0.dll", "libcairo-2.dll",
						"libgdk-win32-2.0-0.dll", "libgtk-win32-2.0-0.dll",
						"libpangocairo-1.0-0.dll", "libpng13.dll"]
                  } 
              }, 
 
    data_files=[
        ("pixmaps/skin/blue", glob.glob("pixmaps/skin/blue/*")),
        ("pixmaps/skin/dark", glob.glob("pixmaps/skin/dark/*")),
        ("pixmaps/skin/default", glob.glob("pixmaps/skin/default/*")),
        ("pixmaps/skin", ""),
        ("pixmaps", ["pixmaps/en.xpm", "pixmaps/it.xpm", "pixmaps/logopyacqua.jpg"]),
        ("files", glob.glob("files/*.txt")),
		("locale", ""),
		("locale/en", ""),
		("locale/en/LC_MESSAGES", ["locale/en/LC_MESSAGES/acqua.mo"]),
		("Plugin", glob.glob("Plugin/*.py"))
    ] 
) 
