```{toctree}
---
hidden: true
maxdepth: 1
---
```

# Stored Product Insect Database

The Stored Product Insect Database (SPIDB) is the Python package to assist with the Stored Product Insect Dataset (SPID) available on Kaggle. The SPID dataset is a collection of recordings made using the Acoustic Stored Product Insect Detection System (A-SPIDS) and the Microwave Stored Product Insect Detection System (M-SPIDS) of several stored product insects at different life stages within various materials under different levels of artificial and natural noise. 

## Background 

## Usage

### Installation

The SPIDB package can be installed using PIP or by downloading the package from GitHub.

```bash
pip install git+https://github.com/dkadyrov/spidb
```

You can download the package from GitHub and install it using the following commands:

```bash
git clone
cd spidb
pip install .
```

### Project Organization

The SPIDB package includes the following directory: 

```plaintext
spidb
+---data
|   |---spi.db
|   +---aspids
|   \---mspids
+---docs
+---examples
+---spidb
```

### Downloading the Datasets from Kaggle

The SPID dataset is available on Kaggle at the following links: 

- A-SPIDS Dataset: [https://www.kaggle.com/dkadyrov/a-spids](https://www.kaggle.com/dkadyrov/a-spids)
- M-SPIDS Dataset: [https://www.kaggle.com/dkadyrov/m-spids](https://www.kaggle.com/dkadyrov/m-spids)

The datasets can be manually downloaded from the Kaggle website or by using the Kaggle API. An [example script](https://github.com/dkadyrov/spidb/tree/main/examples) for downloading the datasets using the Kaggle API is provided in the `examples` folder.

### Models 

The SPIDB package expands on the [SONICDB](https://github.com/dkadyrov/sonicdb) package to include additional models for the dataset. The `SONICDB` package uses the `sqlalchemy` library to interact with a database which is currently a SQLite database. The following figure shows the database schema for the SPID dataset. 

![SPIDB Schema](images/spidb.svg)