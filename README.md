# STIG A View Static
This custom static site generator for [stigaview.com](https://stigaview.com).

## Input
```
products
    rhel7
        product.toml
        v1r1.xml
        v1r2.xml
    rhel8
        product.toml
        v3r1.xml
    ubuntu2004
        product.toml
        v1r1.xml
```

## Usage
You will need Python 3.11+.
On macOS the provided BSD sed will not work for the site maps.
You will need to install GNU sed.

```
$ brew install gnu-sed
```

To build the site run
```
$ make
```

## License
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.
See COPYING for more details.

The STIG content is the public domain.

This program uses code from the Django version of STIG-A-View.
Content is used by permission.
