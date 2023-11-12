# STIG A View Static

## Overview
STIG A View Static is a custom static site geneator.
It takes the manaul STIG released by [DISA](https://public.cyber.mil) and configuration data stored in this repo then converts to website.

## Architecture

### Input
Below is outline of how the products directory works.
```
products
    rhel7
        v1r1.xml
        v1r2.xml
        product.toml
    rhel8
        v3r1.xml
        product.toml
    ubuntu2004
        v1r1.xml
        product.html
```

### Output
The root of the website is in `out`

### Product Configuration
Each product has configuration file called `product.toml` in its respective directory under the `products` directory.
The file contains details about the product and each version of the STIG that the product has.

#### Schema
* `full_name` - The full name for the product with spaces and version number. E.g. `Red Hat Enterprise Linux 9`.
* `short_name` - All lower case name with version. E.g. `rhel9`.

* stigs - a dict of stigs. The key is the DISA version of the STIG, e.g. `v1r1`.
    * stig
        * release_date the release date of the STIG (should be when DISA released on the website not the date in the file) in YYYY-MM-DD format.


### STIG Files
This project only supports the XML files released by DISA in thier lastest format.
This means that files from before 2020 are not supported and will cause the site not to build.

## Usage
You will need Python 3.11+ and `make`.

```
1. `python -m venv venv`
1. `pip install -r requirements.txt`
1. `make`
```

## Adding A New Product
Below is a high level overview.
1. Create a directory with shortname under products.
1. Create a `product.toml` in that directory
1. Add the first STIG xml file.

## License
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.
See COPYING for more details.

The STIG content is the public domain.

This program uses content from the Django version of STIG-A-View.
Content is used by permission.
