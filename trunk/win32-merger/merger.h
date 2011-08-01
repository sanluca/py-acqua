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

#ifndef _MERGER_H_
#define _MERGER_H_

#include <string>

using namespace std;

class Merger
{
public:
	Merger ();
	bool doMerge ();
	
private:
	void mkDirIfNotPresent (const string& dirname);
	bool eraseAtPath (const string& path, bool is_dir);
	bool updateFile (const string& dirname, const string& filename, const string& md5, long long size);

	string hexDigest (const string& filename);
	bool copyFile (const string& orig, const string& dest, bool remove_orig);
	void deleteDirectory (const char *dir);
	
	string m_diff_path;
	string m_update_dir;
};

#endif
