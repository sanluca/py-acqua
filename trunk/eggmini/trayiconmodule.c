/* -*- Mode: C; c-basic-offset: 4 -*- */

/* include this first, before NO_IMPORT_PYGOBJECT is defined */
#include <pygobject.h>

void pytrayicon_register_classes (PyObject *d);

extern PyMethodDef pytrayicon_functions[];

DL_EXPORT(void)
inittrayicon(void)
{
    PyObject *m, *d;
	
    init_pygobject ();

    m = Py_InitModule ("trayicon", pytrayicon_functions);
    d = PyModule_GetDict (m);
	
    pytrayicon_register_classes (d);

    if (PyErr_Occurred ()) {
	Py_FatalError ("can't initialise module trayicon :(");
    }
}
