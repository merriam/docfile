docfile
=======

Hack for managing documents, moving to subdirectories, an batch renames.

This Python 3 program handles documents of named like 
`<dir>_<subdir>_YYYYMMDD<_additional_descriptions>.pdf`, for example `utilities_garbage_20111117_late_2011_12_06_23_37_43.pdf` represents a late 
notice on a garbage bill dated 17-Nov-2011 and scanned on 6-Dec-2011 at 
11:37:43pm (`23_37_43`).   It will get moved into the directory `utilities`, 
subdirectory `garbage`.  Sorting files b)y name orders them by increasing date, 
which makes finding files easy.

My workflow tends to be scanning the files with a ScanSnap scanner, adding the 
category and actual bill date manually, and occasionally running this program 
to move items from the main ScanSnap directory into appropriate subdirectories.

It is placed in the public domain; may it be worth more to you than you paid for it.

Have a wonderful day!
