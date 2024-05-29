"""Summarize Script

This script demonstrates how to summarize the data in the SPIDB database. It illustrates how to query the database, convert the results to a DataFrame, and create pivot tables to summarize the data.
"""

from spidb import spidb, lookup
from dankpy import dankframe
import pandas as pd
import numpy as np

# Initialize the database
db = spidb.Database(r"data/spi.db")

# Get all the logs
logs = db.session.query(spidb.Log).all()

# Get all logs for the ASPIDS sensor
aspids = db.session.query(spidb.Log).filter(spidb.Log.sensor == "ASPIDS").all()

# Convert list of logs to a DataFrame
aspids = dankframe.from_list(aspids)

# Get logs that feature a target using the lookup table
aspids = aspids[aspids.target.isin(lookup.table.keys())]

# Seperate silence and noise logs
silent = aspids[aspids.noise == "Silence"]
noisy = aspids[aspids.noise != "Silence"]

# Create a pivot table for the silent logs
table = pd.pivot_table(
    silent,
    values="duration",
    index="target",
    columns="material",
    aggfunc=np.sum,
    fill_value=0,
)
# Convert the table to minutes
table = table / 60

# Create a pivot table for the noisy logs
table = pd.pivot_table(
    noisy,
    values="duration",
    index="target",
    columns="material",
    aggfunc=np.sum,
    fill_value=0,
)
# Convert the table to minutes
table = table / 60

# Get all logs for the MSPIDS sensor
mspids = db.session.query(spidb.Log).filter(spidb.Log.sensor == "MSPIDS").all()

# Convert list of logs to a DataFrame
mspids = dankframe.from_list(mspids)

# Get logs that feature a target using the lookup table
mspids = mspids[mspids.target.isin(lookup.table.keys())]

# Seperate silence and noise logs
silent = mspids[mspids.noise == "Silence"]
noisy = mspids[mspids.noise != "Silence"]

# Create a pivot table for the silent logs
table = pd.pivot_table(
    silent,
    values="duration",
    index="target",
    columns="material",
    aggfunc=np.sum,
    fill_value=0,
)
table = table / 60

# Create a pivot table for the noisy logs
table = pd.pivot_table(
    noisy,
    values="duration",
    index="target",
    columns="material",
    aggfunc=np.sum,
    fill_value=0,
)
table = table / 60
