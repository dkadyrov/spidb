# %%
from scipy import interpolate, signal
import numpy as np
from dankpy import dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import Rectangle
from matplotlib.patches import Rectangle
# import MinMaxLTTBDownsampler
from matplotlib.patches import Rectangle
from tsdownsample import MinMaxLTTBDownsampler


def detection(internal, external, size):
    result = None

    if internal <= size and internal > 0:
        # if internal <= size:
        result = "Detection"

    # if internal == size:
    # result = "Noise"

    if external >= 1:
        result = "Noise"

    return result


def pulse_information(db, start, length, sensor):
    channels = np.arange(0, 4).tolist()
    peak_index = []
    peak_height = []
    peak_width = []
    peak_prominence = []
    peak_channel = []
    peak_datetime = []

    for c in channels:
        a = db.get_audio(
            start, start + dt.timedelta(seconds=length), channel_number=c, sensor=sensor
        )
        # a.resample(12500)

        a.bandpass_filter(2000, 6000, order=8, overwrite=True)

        a.data.signal = a.envelope()

        a.data.signal = a.data.signal / np.max(np.abs(a.data.signal))

        peaks = signal.find_peaks(
            a.data.signal, height=0.25, prominence=0.25, distance=a.sample_rate / 2
        )
        widths = signal.peak_widths(
            a.data.signal, peaks[0], rel_height=0.9, wlen=a.sample_rate
        )

        peak_index.extend(peaks[0])
        peak_height.extend(peaks[1]["peak_heights"])
        peak_width.extend(widths[0])
        peak_prominence.extend(peaks[1]["prominences"])
        peak_channel.extend([c] * len(peaks[0]))
        peak_datetime.extend(a.data.datetime[peaks[0]])

        # data[c] = {
        #     "peaks": a.data.signal[peaks],
        #     "width": width
        # }

    data = {
        "datetime": peak_datetime,
        "peak_channel": peak_channel,
        "peak_index": peak_index,
        "peak_height": peak_height,
        "peak_width": peak_width,
        "peak_prominence": peak_prominence,
    }

    return data

def threshold_detector(db, 
    start, length=60, internal_cutoff=5, external_cutoff=3, keep_data=True, internal_channels=[0, 1, 2, 3], external_channels=[4,5,6,7]
):


    mo = pd.DataFrame()
    mo["datetime"] = pd.date_range(
        start, start + dt.timedelta(seconds=length), freq="s"
    )
    mo["seconds"] = mo.index
    mo_i = interpolate.interp1d(
        pd.to_numeric(mo.datetime), mo.index, kind="nearest", fill_value="extrapolate"
    )

    channels = np.arange(0, 8).tolist()
    data = pd.DataFrame()  # [{}] * len(channels)

    for c in channels:
        a = db.get_audio(
            start,
            start + dt.timedelta(seconds=length),
            channel_number=int(c),
            sensor="ASPIDS",
        )
        a.resample(12500)

        if c < 4:
            a.bandpass_filter(500, 6000, order=10, overwrite=True)
        else:
            a.highpass_filter(500, order=10, overwrite=True)

        a.envelope(overwrite=True)

        level = np.median(a.data.signal)
        noise = a.data.signal[a.data.signal < level]

        a.data.signal = a.data.signal / (2*np.sqrt(np.mean(noise**2)))

        if "datetime" not in data.columns:
            data["datetime"] = a.data.datetime
        if "time [s]" not in data.columns:
            data["seconds"] = a.data["seconds"]

        mo[f"ch{c}"] = 0 

        if c < 4:
            mo.loc[
                mo_i(a.data[a.data.signal >= internal_cutoff].datetime), f"ch{c}"
            ] = 1
            data[f"ch{c} internal"] = a.data.signal

        else:
            mo.loc[
                mo_i(a.data[a.data.signal >= external_cutoff].datetime), f"ch{c}"
            ] = 1
            data[f"ch{c} external"] = a.data.signal

    mo["internal"] = mo[[f"ch{c}" for c in internal_channels]].sum(axis=1)
    mo["external"] = mo[[f"ch{c}" for c in external_channels]].sum(axis=1)
    mo["detection"] = mo.apply(
        lambda x: detection(x.internal, x.external, size=4), axis=1
    )

    info = {
        "mo": mo,
        "sensor": "ASPIDS",

    }

    if keep_data is True:
        # mo.attrs = {"data": data, "sensor": "ASPIDS"}
        info["data"] = data

    return info

# noise = pd.read_pickle(r"data/noise_500-6000.pkl")

def acoustic_detector(db, 
    start, length=60, internal_cutoff=5, external_cutoff=3, keep_data=True, internal_channels=[0, 1, 2, 3], external_channels=[4,5,6,7]
):

    # metrics = noise.attrs["metrics"]

    mo = pd.DataFrame()
    mo["datetime"] = pd.date_range(
        start, start + dt.timedelta(seconds=length), freq="s"
    )
    mo["seconds"] = mo.index
    mo_i = interpolate.interp1d(
        pd.to_numeric(mo.datetime), mo.index, kind="nearest", fill_value="extrapolate"
    )

    channels = np.arange(0, 8).tolist()
    data = pd.DataFrame()  # [{}] * len(channels)

    for c in channels:
        a = db.get_audio(
            start,
            start + dt.timedelta(seconds=length),
            channel_number=int(c),
            sensor="ASPIDS",
        )
        a.resample(12500)

        if c < 4:
            a.bandpass_filter(500, 6000, order=10, overwrite=True)
        else:
            a.highpass_filter(100, order=10, overwrite=True)

        a.envelope(overwrite=True)

        if c < 4: 
            level = 5*np.median(a.data.signal)
        else: 
            level = 0.5*np.median(a.data.signal)
        
        noise = a.data.signal[a.data.signal < level]
        # a.data.signal = a.data.signal / metrics[f"{int(c)}"]["rms"]

        # if c < 4: 
        a.data.signal = a.data.signal / (np.sqrt(np.mean(noise**2)))
        
        # a.data.signal = 20*np.log10(a.data.signal)
        # else: 
            # a.data.signal = a.data.signal / (np.sqrt(np.mean(noise**2)))            
        if "datetime" not in data.columns:
            data["datetime"] = a.data.datetime
        if "time [s]" not in data.columns:
            data["seconds"] = a.data["seconds"]

        mo[f"ch{c}"] = 0 

        if c < 4:
            mo.loc[
                mo_i(a.data[a.data.signal >= internal_cutoff].datetime), f"ch{c}"
            ] = 1
            data[f"ch{c} internal"] = a.data.signal

        else:
            mo.loc[
                mo_i(a.data[a.data.signal >= external_cutoff].datetime), f"ch{c}"
            ] = 1
            data[f"ch{c} external"] = a.data.signal

        mo[f"ch{c}_max"] = (
            a.data.groupby(pd.Grouper(freq="s", key="datetime"))
            .max()
            .reset_index()["signal"]
        )

    mo["internal"] = mo[[f"ch{c}" for c in internal_channels]].sum(axis=1)
    mo["external"] = mo[[f"ch{c}" for c in external_channels]].sum(axis=1)
    mo["detection"] = mo.apply(
        lambda x: detection(x.internal, x.external, size=4), axis=1
    )

    info = {
        "mo": mo,
        "sensor": "ASPIDS",
    }

    if keep_data is True:
        info["data"] = data

    return info

def acoustic_detector_v3(db, 
    start, length=60, internal_cutoff=5, external_cutoff=3, keep_data=True, internal_channels=[0, 1, 2, 3], external_channels=[4,5,6,7]
):

    # metrics = noise.attrs["metrics"]

    mo = pd.DataFrame()
    mo["datetime"] = pd.date_range(
        start, start + dt.timedelta(seconds=length), freq="s"
    )
    mo["seconds"] = mo.index
    mo_i = interpolate.interp1d(
        pd.to_numeric(mo.datetime), mo.index, kind="nearest", fill_value="extrapolate"
    )

    channels = np.arange(0, 8).tolist()
    data = pd.DataFrame()  # [{}] * len(channels)

    for c in channels:
        a = db.get_audio(
            start,
            start + dt.timedelta(seconds=length),
            channel_number=int(c),
            sensor="ASPIDS",
        )
        a.resample(12500)

        if c < 4:
            a.bandpass_filter(500, 6000, order=10, overwrite=True)
        else:
            a.highpass_filter(100, order=10, overwrite=True)

        a.envelope(overwrite=True)

        if c < 4: 
            level = np.median(a.data.signal)
        else: 
            level = 0.5*np.median(a.data.signal)
        
        noise = a.data.signal[a.data.signal < level]
        # a.data.signal = a.data.signal / metrics[f"{int(c)}"]["rms"]

        # if c < 4: 
        a.data.signal = a.data.signal / (np.sqrt(np.mean(noise**2)))
        
        # a.data.signal = 20*np.log10(a.data.signal)
        # else: 
            # a.data.signal = a.data.signal / (np.sqrt(np.mean(noise**2)))            
        if "datetime" not in data.columns:
            data["datetime"] = a.data.datetime
        if "time [s]" not in data.columns:
            data["seconds"] = a.data["seconds"]

        mo[f"ch{c}"] = 0 

        if c < 4:
            mo.loc[
                mo_i(a.data[a.data.signal >= internal_cutoff].datetime), f"ch{c}"
            ] = 1
            data[f"ch{c} internal"] = a.data.signal

        else:
            mo.loc[
                mo_i(a.data[a.data.signal >= external_cutoff].datetime), f"ch{c}"
            ] = 1
            data[f"ch{c} external"] = a.data.signal

        mo[f"ch{c}_max"] = (
            a.data.groupby(pd.Grouper(freq="s", key="datetime"))
            .max()
            .reset_index()["signal"]
        )

    mo["internal"] = mo[[f"ch{c}" for c in internal_channels]].sum(axis=1)
    mo["external"] = mo[[f"ch{c}" for c in external_channels]].sum(axis=1)
    mo["detection"] = mo.apply(
        lambda x: detection(x.internal, x.external, size=4), axis=1
    )

    info = {
        "mo": mo,
        "sensor": "ASPIDS",
    }

    if keep_data is True:
        info["data"] = data

    return info

def acoustic_detector_v2(db, start, length=60, internal_cutoff=5, external_cutoff=3):
    mo = pd.DataFrame()
    mo["datetime"] = pd.date_range(
        start, start + dt.timedelta(seconds=length), freq="s"
    )
    mo["seconds"] = mo.index
    mo_i = interpolate.interp1d(
        pd.to_numeric(mo.datetime), mo.index, kind="nearest", fill_value="extrapolate"
    )

    noise = pd.read_pickle(r"data/noise1.pkl")

    channels = np.arange(0, 8).tolist()
    data = pd.DataFrame()  # [{}] * len(channels)

    for c in channels:
        metrics = noise.attrs["metrics"][f"{int(c)}"]

        a = db.get_audio(
            start,
            start + dt.timedelta(seconds=length),
            channel_number=int(c),
            sensor="Acoustic",
        )
        a.resample(12500)

        if c < 4:
            # a.bandpass_filter(1000, 4000, order=8, overwrite=True)
            a.bandpass_filter(2000, 6000, order=8, overwrite=True)
        else:
            a.highpass_filter(100, order=8, overwrite=True)
            # a.bandpass_filter(1500, 4000, order=8, overwrite=True)

        a.fade_in(fade_time=1, overwrite=True)
        a.fade_out(fade_time=1, overwrite=True)
        a.data.signal = a.envelope()

        cutoff = metrics["max"] / metrics["rms"]

        a.data.signal = a.data.signal / metrics["rms"]

        # if c >= 4:
        # level = 8.5 * np.median(a.data.signal)
        # noise = a.data.signal[a.data.signal < level]

        # if c == 7:
        # print("pause here")

        # a.data.signal = a.data.signal / np.sqrt(np.mean(noise ** 2))

        if "datetime" not in data.columns:
            data["datetime"] = a.data.datetime
        if "time [s]" not in data.columns:
            data["seconds"] = a.data["seconds"]
            # if c < 4:
        #     data[c * 2] = {
        #         "datetime": a.data.datetime,
        #         "time [s]": a.data["seconds"],
        #         "signal": a.data.signal,
        #         "label": f"Ch{c} Piezo",
        #     }

        # else:
        #     data[c - (7 - c)] = {
        #         "datetime": a.data.datetime,
        #         "time [s]": a.data["seconds"],
        #         "signal": a.data.signal,
        #         "label": f"Ch{c} Microphone",
        #     }
        # mo_a = interpolate.interp1d(
        #     pd.to_numeric(a.data.datetime), a.data.signal, kind="linear", fill_value="extrapolate"
        # )

        # mo[f"ch{c}_max"] = mo.datetime.apply(lambda x: a.data.signal[(a.data.datetime >= x) & (a.data.datetime <= x + dt.timedelta(seconds=1))].max())

        mo[f"ch{c}_max"] = (
            a.data.groupby(pd.Grouper(freq="S", key="datetime"))
            .max()
            .reset_index()["signal"]
        )

        mo[f"ch{c}_pulses"] = a.data.groupby(pd.Grouper(freq="S", key="datetime"))[
            "signal"
        ].agg(lambda x: ((x >= internal_cutoff) * 1).sum())

        # mo[f"ch{c}_width"] = mo[f"ch{c}_max"].apply(lambda x: signal.peak_widths(a.data.signal, a.data.signal[a.data.signal == x].index)[0][0])

        if c < 4:
            mo.loc[
                mo_i(a.data[a.data.signal >= internal_cutoff].datetime), f"ch{c}"
            ] = 1
            data[f"ch{c} internal"] = a.data.signal

        else:
            mo.loc[
                mo_i(a.data[a.data.signal >= external_cutoff].datetime), f"ch{c}"
            ] = 1
            data[f"ch{c} external"] = a.data.signal

    mo["internal"] = mo[[f"ch{c}" for c in range(4)]].sum(axis=1)
    mo["external"] = mo[[f"ch{c}" for c in [7]]].sum(axis=1)
    # mo["external"] = mo[[f"ch{c}" for c in [range(4, 8)]]].sum(axis=1)
    mo["detection"] = mo.apply(
        lambda x: detection(x.internal, x.external, size=4), axis=1
    )

    mo.attrs = {"data": data, "sensor": "Acoustic"}

    return mo


def microwave_detector(db, start, length=60, internal_cutoff=5, external_cutoff=10):
    data = []

    mo = pd.DataFrame()
    mo["datetime"] = pd.date_range(
        start, start + dt.timedelta(seconds=length), freq="s"
    )
    mo["seconds"] = mo.index
    mo_i = interpolate.interp1d(
        pd.to_numeric(mo.datetime), mo.index, kind="nearest", fill_value="extrapolate"
    )

    channels = np.arange(0, 8).tolist()
    for c in channels:
        a = db.get_audio(
            start, start + dt.timedelta(seconds=length), channel_number=c, sensor="Microwave"
        )

        mo[f"ch{c}"] = 0
        if c < 6:
            a.resample(1000)
            a.lowpass_filter(100, order=8, overwrite=True)
            env = a.envelope()

            level = 2 * np.median(env)
            noise = env[env < level]
            env = env / np.sqrt(np.mean(noise**2))

            data.append(
                {
                    "datetime": a.data.datetime,
                    "time [s]": a.data["seconds"],
                    "signal": env,
                    "label": f"Ch{c} Microwave",
                }
            )

            mo.loc[mo_i(a.data[env > internal_cutoff].datetime), f"ch{c}"] = 1

        else:
            a.resample(8000)

            a.bandpass_filter(50, 300, order=4, overwrite=True)

            env = a.envelope()
            level = 2 * np.median(env)
            noise = env[env < level]

            env = env / np.sqrt(np.mean(noise**2))

            data.append(
                {
                    "datetime": a.data.datetime,
                    "time [s]": a.data["seconds"],
                    "signal": env,
                    "label": f"Ch{c} Microphone" if c == 6 else f"Ch{c} Piezo",
                }
            )

            mo.loc[mo_i(a.data[env > external_cutoff].datetime), f"ch{c}"] = 1

    mo["internal"] = mo[[f"ch{c}" for c in range(6)]].sum(axis=1)
    mo["external"] = mo[[f"ch{c}" for c in range(6, 8)]].sum(axis=1)
    mo["detection"] = mo.apply(
        lambda x: detection(x.internal, x.external, size=6), axis=1
    )

    return data, mo


# %%

def detection_display(mo, IDT=26, NDT=13, time_format="datetime", style="minimal", sensor="ASPIDS"):
    # NDT = round(IDT / 2)
    data = mo["data"]
    mo = mo["mo"]

    # if style=="minimal":

    # fig, axs = plt.subplots(nrows=len(data)+1, ncols=1, sharex=True, figsize=(1.5*6, 1.5*6), layout="compressed")

    # fig, axs = plt.subplots(nrows=len(data)+1, ncols=1, sharex=True, figsize=(1.5*11.5, 1.5*4.76), layout="compressed")

    # fig, axs = plt.subplots(nrows=len(data)+1, ncols=1, sharex=True, layout="compressed")

    # mo.datetime = mo.datetime - dt.timedelta(seconds=1)
    mo = mo[mo.datetime >= data["datetime"].min()]
    mo = mo[mo.datetime <= data["datetime"].max()]

    internal = data.loc[:, data.columns.str.contains("internal")]
    external = data.loc[:, data.columns.str.contains("external")]

    internal.columns = internal.columns.str.replace(" internal", "")
    external.columns = external.columns.str.replace(" external", "")

    if sensor.name == "ASPIDS":
        fig, axs = plt.subplots(
            nrows=6,
            ncols=1,
            sharex=True,
            # layout="compressed",
            figsize=(6, 4.15),
        )  # mdpi
    if sensor.name == "MSPIDS":
        fig, axs = plt.subplots(
            nrows=7,
            ncols=1,
            sharex=True,
            layout="compressed",
            figsize=(6, (5.6 / 1.6180) * (4 / 2)),
        )

    for i in range(len(internal.columns)):
        ax = axs[i]
        row = internal.iloc[:, i]

        s_ds = MinMaxLTTBDownsampler().downsample(data["datetime"], row, n_out=1000)

        if time_format == "datetime":
            ax.plot(data["datetime"].values[s_ds], row.values[s_ds])
            eligble = mo[mo[row.name] == 1].datetime
            width = 1.1574074074074075e-05
        else:
            ax.plot(data["seconds"].values[s_ds], row.values[s_ds])
            eligble = mo[mo[row.name] == 1]["seconds"]
            width = 1

        ax.bar(
            eligble,
            height=10,
            width=width,
            color="red",
            align="center",
            bottom=90,
            clip_on=True,
            zorder=10,
        )
        # ax.bar(eligble, height=10, width=width, color="red", align="center", bottom=90, clip_on=True, zorder=10)
        ax.set_ylabel(f"Ch. {i}")

    if sensor.name == "ASPIDS":
        ax = axs[i + 1]
        row = external.iloc[:, 3]
        s_ds = MinMaxLTTBDownsampler().downsample(data["datetime"], row, n_out=1000)
        if time_format == "datetime":
            ax.plot(data["datetime"][s_ds], row[s_ds])
            eligble = mo[mo[row.name] == 1].datetime
            width = 1.1574074074074075e-05
        else:
            ax.plot(data["seconds"][s_ds], row[s_ds])
            eligble = mo[mo[row.name] == 1]["seconds"]
            width = 1

        ax.bar(
            eligble,
            height=10,
            width=width,
            color="blue",
            align="center",
            bottom=90,
            clip_on=True,
            zorder=10,
        )
        # ax.bar(eligble, height=10, width=width, color="blue", align="center", bottom=90, clip_on=True, zorder=10)
        ax.set_ylabel("Mic.")

    for i in range(len(axs) - 1):
        ax = axs[i]
        ax.yaxis.set_label_position("right")
        # ax.set_ylim([0, 100])
        # ax.set_yticks([0, 50, 100])
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 50, 100])

        if time_format == "datetime":
            myFmt = mdates.DateFormatter("%H:%M:%S")
            ax.xaxis.set_major_formatter(myFmt)
            ax.xaxis.set_minor_locator(mdates.SecondLocator(interval=1))
            ax.set_xlim([min(data["datetime"]), max(data["datetime"])])
        else:
            ax.set_xlim([min(data["seconds"]), round(max(data["seconds"]))])

    # for i in range(len(data)):
    #     ax = axs[i]
    #     row = data[i]

    #     s_ds = MinMaxLTTBDownsampler().downsample(row["datetime"], row["signal"], n_out = 1000)

    #     if method == "datetime":
    #         ax.plot(row["datetime"][s_ds], row["signal"][s_ds])
    #         eligble = mo[mo[f"{row['label'][:3].lower()}"] == 1].datetime
    #         width = 1.1574074074074075e-05
    #     else:
    #         ax.plot(row["seconds"][s_ds], row["signal"][s_ds])
    #         eligble = mo[mo[f"{row['label'][:3].lower()}"] == 1]["seconds"]
    #         width = 1

    #     if "Microphone" in row["label"]:
    #         ax.bar(eligble, height=1, width=width, color="blue", align="center", bottom=19, clip_on=True, zorder=10)
    #         # ax.scatter(eligble, [20]*len(eligble), marker="s", c="blue", s=10, alpha=1, clip_on=False, zorder=10)
    #     elif row["label"] == "Ch7 Piezo":
    #         ax.bar(eligble, height=1, width=width, color="blue", align="center", bottom=19, clip_on=True, zorder=10)
    #         # ax.scatter(eligble, [20]*len(eligble), marker="s", c="blue", s=10, alpha=1, clip_on=False, zorder=10)
    #     else:
    #         # ax.scatter(eligble, [20]*len(eligble), marker="s", c="red", s=10, alpha=1, clip_on=False, zorder=10)
    #         ax.bar(eligble, height=1, width=width, color="red", align="center", bottom=19, clip_on=True, zorder=10)

    #     # ax.plot(row["datetime"], row["signal"])
    #     ax.set_ylabel(row["label"], rotation=0, horizontalalignment='left')
    #     ax.yaxis.set_label_position("right")
    #     ax.set_ylim([0, 20])
    #     ax.set_yticks([0, 10, 20])

    #     if method == "datetime":
    #         myFmt = mdates.DateFormatter('%H:%M:%S')
    #         ax.xaxis.set_major_formatter(myFmt)
    #         ax.xaxis.set_minor_locator(mdates.SecondLocator(interval=1))
    #         ax.set_xlim([min(row["datetime"]), max(row["datetime"])])
    #     else:
    #         # ax.set_xlim([round(row[""].min()), round(times.max())])
    #         ax.set_xlim([min(row["seconds"]), round(max(row["seconds"]))])

    #     ax.get_yaxis().set_label_coords(1.01, 0.6)

    ax = axs[-1]
    hits = mo[mo["detection"] == "Detection"]
    false_flags = mo[mo["detection"] == "Noise"]
    clean = mo[mo.detection.isna()]

    if time_format == "datetime":
        ax.bar(
            clean.datetime,
            height=1,
            width=width,
            color="green",
            align="center",
            clip_on=True,
            zorder=1,
        )
        ax.bar(
            hits.datetime,
            height=1,
            width=width,
            color="red",
            align="center",
            clip_on=True,
            zorder=2,
        )
        ax.bar(
            false_flags.datetime,
            height=1,
            width=width,
            color="blue",
            align="center",
            clip_on=True,
            zorder=3,
        )
    elif time_format == "seconds":
        ax.bar(
            clean.index.tolist(),
            height=1,
            width=width,
            color="green",
            align="center",
            clip_on=True,
            zorder=1,
        )
        ax.bar(
            hits.index.tolist(),
            height=1,
            width=width,
            color="red",
            align="center",
            clip_on=True,
            zorder=2,
        )
        ax.bar(
            false_flags.index.tolist(),
            height=1,
            width=width,
            color="blue",
            align="center",
            clip_on=True,
            zorder=3,
        )

    # ax.scatter(hits.datetime, [1]*len(hits), s=10, c="green", marker="s")
    # ax.scatter(false_flags.datetime, [1]*len(false_flags), s=10, c="red", marker="s")
    ax.set_ylim([0, 1])
    ax.set_yticklabels([])
    ax.set_yticks([])
    fig.align_ylabels()
    ax.yaxis.set_label_position("right")

    if time_format == "datetime":
        fig.supxlabel(f"Time on {data['datetime'][0].date()}")
    else:
        fig.supxlabel("Time [s]")

    fig.supylabel("Relative Normalized Amplitude")

    ax = axs[0]

    values = mo["detection"].value_counts()
    if "Noise" in values.index and values["Noise"] >= NDT:
        text = "Noise"
        color = "blue"
    elif "Detection" in values.index and values["Detection"] >= IDT:
        text = "Infested"
        color = "red"
    else:
        text = "Clean"
        color = "green"
    # check number of detections in the detection column

    ax.add_patch(
        Rectangle(
            (0, 150),
            len(mo) - 1,
            100,
            facecolor=color,
            clip_on=False,
            linewidth=1,
            edgecolor="black",
            fill=True,
        )
    )
    ax.text(
        (len(mo) - 1) / 2,
        200,
        text,
        fontsize=18,
        zorder=5,
        color="white",
        horizontalalignment="center",
        verticalalignment="center_baseline",
        fontweight="bold",
    )

    # ax.add_patch(Rectangle((0,150), 60, 100,facecolor=color,
    #                           clip_on=False,linewidth = 1, edgecolor="black", fill=True))
    # ax.text(30, 200, text, fontsize = 20 ,zorder = 5, fontweight="extra bold", fontstretch="ultra-expanded",
    #             color = 'white', horizontalalignment="center", verticalalignment="center_baseline")

    return fig, axs