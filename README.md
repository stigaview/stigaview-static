# STIG A View Static

## Input
```
input
    rhel7
        v1r1.xml
        v1r2.xml
    rhel8
        v3r1.xml
    ubuntu2004
```

## Usage
You will need Python 3.11+.

```
$ python -m python -m stigaview_static -o out products
```

## License
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.
See COPYING for more details.

The STIG content is the public domain.

This program uses content from the Django version of STIG-A-View.
Content is used by permission.
