# Downloading Dataset

## Initializing the Database

The SPIDB package uses the `SONICDB` package to interact with the SQLite database. The database can be initialized using the following command:

```python
from spidb import spidb 

db = spidb.Database("data/spi.db")
```


## Stored Product Insect Dataset

The Stored Product Insect Dataset (SPID) is available on Kaggle at the following links: 

- A-SPIDS Dataset[^aspids]: [https://www.kaggle.com/dkadyrov/a-spids](https://www.kaggle.com/dkadyrov/a-spids)
- M-SPIDS Dataset[^mspids]: [https://www.kaggle.com/dkadyrov/m-spids](https://www.kaggle.com/dkadyrov/m-spids)

The datasets can be manually downloaded from the Kaggle website or by using the Kaggle API. An [example script](https://github.com/dkadyrov/spidb/tree/main/examples) for downloading the datasets using the Kaggle API is provided in the `examples` folder.

The datasets should be downloaded and extracted into the `data` directory of the SPIDB package. The following is the directory structure for the SPIDB package to work out of the box with the examples provided in the package:

```none
spidb 
+---data
|   |---spi.db
|   +---aspids
|   \---mspids
```

The data can be downloaded into a seperate directory a new database will need to be generated and populated with the updated filepaths. An example of this script is available in the `examples` folder.

## BugBytes Dataset

The BugBytes dataset[^bugbytes] is a collection of recordings made using the Acoustic Stored Product Insect Detection System (A-SPIDS) and the Microwave Stored Product Insect Detection System (M-SPIDS) of several stored product insects at different life stages within various materials under different levels of artificial and natural noise. The dataset is available on Kaggle at the following link: [BugBytes](https://www.kaggle.com/dkadyrov/bugbytes).

```none
spidb 
+---data
|   |---bugbytes.db
|   \---bugbytes
```


[^aspids]: Daniel Kadyrov, Alexander Sutin, Alexander Sedunov, Nikolay Sedunov, and Hady Salloum, “Stored Product Insect Dataset (SPID) - ASPIDS.” Kaggle. doi: 10.34740/KAGGLE/DS/4982480.

[^mspids]: Daniel Kadyrov, Alexander Sutin, Alexander Sedunov, Nikolay Sedunov, and Hady Salloum, “Stored Product Insect Dataset (SPID) - MSPIDS.” Kaggle. doi: 10.34740/KAGGLE/DSV/8618204.

[^bugbytes]: R. Mankin, “Bug Bytes Sound Library: Stored Product Insect Pest Sounds.” Ag Data Commons, 2019. doi: 10.15482/USDA.ADC/1504600.
