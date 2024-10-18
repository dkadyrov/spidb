#%%
import kaggle

# To generate an API token, follow instructions here: https://github.com/Kaggle/kaggle-api/blob/main/docs/README.md
kaggle.api.authenticate()

#%%
# Download A-SPIDS dataset
# kaggle.api.dataset_download_files('Stored Product Insect Dataset (SPID) - ASPIDS', path='data', unzip=True)
#%%
# Download M-SPIDS dataset
kaggle.api.dataset_download_files('sanlian/app-store-reviews-for-a-mobile-app', path='data/', unzip=True)
# %%
