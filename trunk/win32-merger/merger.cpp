// Copyright (C) 2007 Francesco Piccinno. All rights reserved.
//
// This file is part of PyAcqua application
//
// This file may be distributed and/or modified under the terms of the
// GPL license appearing in the file LICENSE included in the
// packaging of this file.
// This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
// WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
//

#include "merger.h"

#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <windows.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <direct.h>

#include "tinyxml/tinyxml.h"
#include "md5.h"

Merger::Merger () : m_update_dir (getenv ("APPDATA")), m_diff_path ("")
{
	m_update_dir += "\\.pyacqua\\update";
	m_diff_path = m_update_dir + "\\.diff.xml";
}

bool Merger::doMerge ()
{
	TiXmlDocument doc (m_diff_path.c_str ());
	
	if (!doc.LoadFile ())
		return false;
	
	bool all_ok = true;
	TiXmlHandle hDoc (&doc);
	TiXmlElement *pElem, *pChildElem;
	TiXmlHandle hRoot(0);
	
	pElem = hDoc.FirstChildElement ().Element ();
	
	if (!pElem || pElem->ValueStr () != "pyacqua")
		return false;
	
	hRoot = TiXmlHandle (pElem);
	pElem = hRoot.FirstChild ().Element ();
	
	for (pElem; pElem; pElem = pElem->NextSiblingElement ())
	{
		bool to_delete = false;
		
		if (pElem->ValueStr () != "directory")
			continue;
		
		string dirname = pElem->Attribute ("name");
		
		if (dirname.substr (0, 2) == "$$" &&
		    dirname.substr (dirname.length () - 2) == "$$")
			to_delete = true;
		
		hRoot = TiXmlHandle (pElem);
		pChildElem = hRoot.FirstChild ().Element ();
		
		if (to_delete)
			dirname = dirname.substr (2, dirname.length () - 4);
		else
		    mkDirIfNotPresent (dirname);
		
		for (pChildElem; pChildElem; pChildElem = pChildElem->NextSiblingElement ())
		{
			if (pChildElem->ValueStr () != "file")
				continue;
			
			string md5      = pChildElem->Attribute ("md5");
			string filename = pChildElem->Attribute ("name");
			string bytes    = pChildElem->Attribute ("bytes");
			
			long long size = ::atoll (bytes.c_str ());
			
			//cout << "String: " << bytes << " Value: " << size << endl;
			
			if (to_delete)
				eraseAtPath (dirname + "\\" + filename, false);
			else
				if (!updateFile (dirname, filename, md5, size))
				{
					all_ok = false;
					break;
				}
		}
		
		if (to_delete)
		    eraseAtPath (dirname, true);
	}
	
	if (all_ok)
		deleteDirectory (m_update_dir.c_str ());
	else
		::remove (m_diff_path.c_str ());
	
	system ("pause");
	
	return all_ok;
}

void Merger::mkDirIfNotPresent (const string& dirname)
{
	cout << ">> Controllo directory: " << dirname << " ... ";
	
	struct _stat dir_stat;
	
	if (!::_stat (dirname.c_str (), &dir_stat))
	{
		// controlla se e' una dir
		if (S_ISDIR (dir_stat.st_mode))
		{
			cout << "ok." << endl;
			return;
		}
		
		cout << "Uhm.. e' un file?" << endl;
	}
	else
	{
		::mkdir (dirname.c_str ());
		cout << "creata." << endl;
	}
}

bool Merger::eraseAtPath (const string& path, bool is_dir)
{
	if (!is_dir)
	{
		cout << ">> Rimozione file " << path << endl;
		if (::remove (path.c_str ()) != 0)
			return false;
		return true;
	}
	else
	{
		char newsub[MAX_PATH];
		char newdir[MAX_PATH];
		char fname[MAX_PATH];
		
		HANDLE hList;
		
		TCHAR szDir[MAX_PATH];
		WIN32_FIND_DATA FileData;
		
		string dirpath (path);
		dirpath += "\\*";
		hList = FindFirstFile (szDir, &FileData);
		
		if (hList == INVALID_HANDLE_VALUE)
			return false;
		
		do {
			strncpy (fname, FileData.cFileName, MAX_PATH);
			
			if (!strcmp (fname,".") || !strcmp (fname,".."))
				continue;
			else
				return false;
		} while (FindNextFile (hList, &FileData));
		
		FindClose (hList);
		
		cout << ">> Directory vuota: " << path << " elimino." << endl;
		::remove (path.c_str ()); // ce ne sbattiamo se genera un errore o meno
		
		return true;
	}
}

bool Merger::updateFile (const string& dirname, const string& filename, const string& md5, long long size)
{
	if (filename.empty ())
		return false;
	
	string path (dirname == "." ? m_update_dir : m_update_dir + "\\" + dirname);
	path += "\\" + filename;
	
	cout << path << endl;
	
	string new_md5 = hexDigest (m_update_dir + "\\" + filename);
	long new_size = -1;

	struct _stat filestat;
	if (::_stat (filename.c_str (), &filestat) == 0)
		new_size = filestat.st_size;
	else
		new_size = -1;
	
	cout << ">> Controllo file:" << filename << endl;
	cout << "     MD5: " << md5 << " == " << new_md5 << endl;
	//cout << "   siz: " << size << " == " << new_size << endl;
	
	if (/*new_size == size &&*/ new_md5 == md5)
	{
		cout << ">> Checksum ok ;-)" << endl;
		copyFile (path, filename, true);
		return true;
	}
	else
	{
		cout << "!! Errore nel checksum :-\\" << endl;
		return false;
	}
}

string Merger::hexDigest (const string& filename)
{
	md5_state_t context;
	MD5 hasher;
	
	unsigned char buff[1024], digest[16];
	
	ifstream file;
	file.open (filename.c_str (), ios::in | ios::binary);
	
	if (!file.good ())
		return "";
	
	hasher.Init (&context);
	
	while (file.good ())
	{
		file.read ((char *)buff, 1024);
		hasher.Append (&context, buff, file.gcount ());
	}
	
	hasher.Finish (digest, &context);
	
	file.close ();
	
	char temp[32];
	
	int p = 0;
	for (int i = 0; i < 16; i++)
	{
		::sprintf (&temp[p], "%02x", digest[i]);
		p += 2;
	}
	
	return string (temp);
}

bool Merger::copyFile (const string& orig, const string& dest, bool remove_orig)
{
	cout << ">> File copiato: " << dest << endl;
	
	ifstream ifs (orig.c_str (), ios::in | ios::binary);
	ofstream ofs (dest.c_str (), ios::out | ios::binary);
	
	char buff[4096];
	int readbytes = 1;
	
	while (readbytes != 0)
	{
		ifs.read (buff, sizeof (buff));
		readbytes = ifs.gcount ();
		ofs.write (buff, readbytes);
	}
	
	ifs.close ();
	ofs.close ();
	
	if (remove_orig)
		::remove (orig.c_str ());
}

void Merger::deleteDirectory (const char *dir)
{
	char fpath[MAX_PATH];
	char fname[MAX_PATH];
	
	HANDLE hList;
	TCHAR szDir[MAX_PATH];
	WIN32_FIND_DATA FileData;
	::snprintf (szDir, MAX_PATH, "%s\\*", dir);
	hList = FindFirstFile (szDir, &FileData);
	
	if (hList == INVALID_HANDLE_VALUE)
		return;
	
	do {
		::strncpy (fname, FileData.cFileName, MAX_PATH);
		
		if (!::strcmp (fname, ".")) continue;
		if (!::strcmp (fname, "..")) continue;
		
		::snprintf (fpath, MAX_PATH, "%s\\%s", dir, fname);
		if (FileData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
			deleteDirectory (fpath);
		else
			DeleteFile (fpath);
	
	} while (FindNextFile (hList, &FileData));
	
	FindClose (hList);
	RemoveDirectory (dir);
	return;
}
