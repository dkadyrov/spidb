# %%
import os

os.makedirs(r"data/kaggle/ASPID", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID", exist_ok=True)

os.makedirs(r"data/kaggle/ASPID/spectrograms", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/spectrograms", exist_ok=True)
os.makedirs(r"data/kaggle/ASPID/envelopes", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/envelopes", exist_ok=True)

os.makedirs(r"data/kaggle/ASPID/spectrograms/binary", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/spectrograms/binary", exist_ok=True)
os.makedirs(r"data/kaggle/ASPID/envelopes/binary", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/envelopes/binary", exist_ok=True)

os.makedirs(r"data/kaggle/ASPID/spectrograms/multiclass", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/spectrograms/multiclass", exist_ok=True)
os.makedirs(r"data/kaggle/ASPID/envelopes/multiclass", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/envelopes/multiclass", exist_ok=True)

os.makedirs(r"data/kaggle/ASPID/spectrograms/binary/insect", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/spectrograms/binary/insect", exist_ok=True)
os.makedirs(r"data/kaggle/ASPID/envelopes/binary/insect", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/envelopes/binary/insect", exist_ok=True)


os.makedirs(r"data/kaggle/ASPID/spectrograms/binary/no_insect", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/spectrograms/binary/no_insect", exist_ok=True)
os.makedirs(r"data/kaggle/ASPID/envelopes/binary/no_insect", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/envelopes/binary/no_insect", exist_ok=True)

os.makedirs(r"data/kaggle/ASPID/spectrograms/multiclass/no_insect", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/spectrograms/multiclass/no_insect", exist_ok=True)
os.makedirs(r"data/kaggle/ASPID/envelopes/multiclass/no_insect", exist_ok=True)
os.makedirs(r"data/kaggle/MSPID/envelopes/multiclass/no_insect", exist_ok=True)


# %%
# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/ASPIDS", exist_ok=True)
# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/MSPIDS", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/ASPIDS/binary", exist_ok=True)
# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/MSPIDS/binary", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/ASPIDS/binary/insect", exist_ok=True)
# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/MSPIDS/binary/insect", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/ASPIDS/binary/no_insect", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/MSPIDS/binary/no_insect", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/ASPIDS/multiclass", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/MSPIDS/multiclass", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/ASPIDS/multiclass/no_insect", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/spectrograms/MSPIDS/multiclass/no_insect", exist_ok=True)

# #%%
# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/ASPIDS", exist_ok=True)
# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/MSPIDS", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/ASPIDS/binary", exist_ok=True)
# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/MSPIDS/binary", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/ASPIDS/binary/insect", exist_ok=True)
# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/MSPIDS/binary/insect", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/ASPIDS/binary/no_insect", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/MSPIDS/binary/no_insect", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/ASPIDS/multiclass", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/MSPIDS/multiclass", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/ASPIDS/multiclass/no_insect", exist_ok=True)

# os.makedirs(r"C:/Users/daniel/Documents/SPIDS/data/envelopes/MSPIDS/multiclass/no_insect", exist_ok=True)
# #%%


# # os.makedirs(r"G:/My Drive/Envelopes/", exist_ok=True)

# # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/", exist_ok=True)
# # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/", exist_ok=True)

# # # %%

# # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/binary/", exist_ok=True)
# # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/binary/", exist_ok=True)

# # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/binary/insect", exist_ok=True)
# # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/binary/insect", exist_ok=True)

# # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/binary/no_insect", exist_ok=True)
# # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/binary/no_insect", exist_ok=True)


# # # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/binary/spectrogram_channel", exist_ok=True)
# # # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/binary/spectrogram_channel", exist_ok=True)
# # # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/binary/spectrogram_full", exist_ok=True)
# # # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/binary/spectrogram_full", exist_ok=True)

# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/ASPIDS/binary/spectrogram_channel/insect", exist_ok=True
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/MSPIDS/binary/spectrogram_channel/insect", exist_ok=True
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/ASPIDS/binary/spectrogram_full/insect", exist_ok=True
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/MSPIDS/binary/spectrogram_full/insect", exist_ok=True
# # # )

# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/ASPIDS/binary/spectrogram_channel/no_insect", exist_ok=True
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/MSPIDS/binary/spectrogram_channel/no_insect", exist_ok=True
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/ASPIDS/binary/spectrogram_full/no_insect", exist_ok=True
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/MSPIDS/binary/spectrogram_full/no_insect", exist_ok=True
# # # )

# # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/multiclass/", exist_ok=True)
# # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/multiclass/", exist_ok=True)

# # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/multiclass/no_insect", exist_ok=True)
# # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/multiclass/no_insect", exist_ok=True)
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/ASPIDS/multiclass/spectrogram_channel", exist_ok=True
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/MSPIDS/multiclass/spectrogram_channel", exist_ok=True
# # # )
# # # os.makedirs(r"G:/My Drive/Envelopes/ASPIDS/multiclass/spectrogram_full", exist_ok=True)
# # # os.makedirs(r"G:/My Drive/Envelopes/MSPIDS/multiclass/spectrogram_full", exist_ok=True)


# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/ASPIDS/multiclass/spectrogram_channel/no_insect",
# # #     exist_ok=True,
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/MSPIDS/multiclass/spectrogram_channel/no_insect",
# # #     exist_ok=True,
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/ASPIDS/multiclass/spectrogram_full/no_insect", exist_ok=True
# # # )
# # # os.makedirs(
# # #     r"G:/My Drive/Envelopes/MSPIDS/multiclass/spectrogram_full/no_insect", exist_ok=True
# # # )
