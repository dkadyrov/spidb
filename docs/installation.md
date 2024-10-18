# Installation

The SPIDB package can be installed using PIP or by downloading the package from GitHub.

## Installation using PIP

The package can be installed using the following command:

```bash
pip install git+https://github.com/dkadyrov/spidb
```

There is no plan to release the package on PyPI at this time.

## Installation from GitHub

You can download the package from GitHub and install it using the following commands:

```bash
git clone https://github.com/dkadyrov/spidb
cd spidb
pip install .
```

## Dependencies

The SPIDB package only depends on the `SONICDB` package, a Python package developed by the author to manage acoustic data in relational databases through `SQLAlchemy` syntax. The `SONICDB` package is available on GitHub at the following link: [SONICDB](https://github.com/dkadyrov/sonicdb).

## Project Structure

```none
+---.github
+---data
+---docs
+---examples
+---spidb
|   |   spidb.py
```
