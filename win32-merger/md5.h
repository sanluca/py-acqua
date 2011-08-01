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

#ifndef _MD5_H_
#define _MD5_H_

#include <string>

typedef unsigned char *md5_byte_t;

typedef struct 
{
	unsigned long int state[4];
	unsigned long int count[2];
	unsigned char buffer[64];
} md5_state_t;

class MD5
{
private:
	void Transform (unsigned long int state[4], unsigned char block[64]);
	void Encode (unsigned char*, unsigned long int*, unsigned int);
	void Decode (unsigned long int*, unsigned char*, unsigned int);
public:
	MD5 () {};
	void Init (md5_state_t*);
	void Append (md5_state_t*, unsigned char*, unsigned int);
	void Finish (unsigned char [16], md5_state_t*);
};

#endif

