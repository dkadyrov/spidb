# %%
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Patch
from sonicdb import audio

from spidb import normalization, spidb
from dankpy import acoustics

def detection_algorithm(internal: int, external: int, size: int) -> str:
    """
    Detection algorithm

    Args:
        internal (int): internal value
        external (int): external value
        size (int): size value

    Returns:
        str: result
    """
    result = None

    if internal < size and internal > 0:
        if external >= 1:
            result = "Noise"

        else: 
            result = "Insect"

    if internal == size:
        result = "Noise"

    return result


def classification_algorithm(detection: pd.Series | list, DT: int, NT: int) -> str:
    """
    Classification algorithm

    Args:
        detection (pd.Series|list): detection values
        DT (int): Detection threshold
        NT (int): Noise threshold

    Returns:
        str: result
    """

    # The detection variable is a list or pandas series with the values as None, Insect, or Noise. If the number of Insect values is greater than the detection threshold, the outcome is Insect. If the number of Noise values is greater than the noise threshold, the outcome is Noise. Otherwise, the outcome is None.

    outcome = "Clean"

    if (detection == "Insect").sum() >= DT:
        outcome = "Insect"

    if (detection == "Noise").sum() >= NT:
        outcome = "Noise"

    return outcome


def classifier(insect_number, noise_number, DT, NT):
    """
    Classifier

    Args:
        insect_number (int): number of insects detections
        noise_number (int): number of noise detections
        DT (int): Detection threshold
        NT (int): Noise threshold

    Returns:
        str: result
    """
    result = "None"

    if insect_number >= DT:
        result = "Insect"

    if noise_number >= NT:
        result = "Noise"

    return result


def robust_scale(data):
    median = np.median(data)
    iqr = np.percentile(data, 75) - np.percentile(data, 25)
    return (data - median) / (
        iqr + 1e-6
    )  # Adding a small value to avoid division by zero


def acoustic_detection(
    db: spidb.Database,
    sensor: int | spidb.models.Sensor | str,
    start: datetime,
    length: int = 60,
    internal_cutoff: int = 5,
    external_cutoff: int = 5,
    internal_channels: list = [0, 1, 2, 3],
    external_channels: list = [7],
):
    """
    Acoustic detection algorithm

    Args:
        db (spidb.Database): database object
        sensor (int | spidb.models.Sensor | str): sensor object
        start (datetime): start datetime
        length (int, optional): _description_. Defaults to 60.
        internal_cutoff (int, optional): _description_. Defaults to 5.
        external_cutoff (int, optional): _description_. Defaults to 5.
        internal_channels (list, optional): _description_. Defaults to [0, 1, 2, 3].
        external_channels (list, optional): _description_. Defaults to [6].
    """

    mo = pd.DataFrame()

    channels = internal_channels + external_channels

    if isinstance(sensor, int):
        sensor = db.session.get(spidb.Sensor, sensor)
    elif isinstance(sensor, str):
        sensor = (
            db.session.query(spidb.Sensor).filter(spidb.Sensor.name == sensor).first()
        )

    for channel in channels:
        a = db.get_audio(
            start=start,
            end=start + timedelta(seconds=length),
            sensor=sensor,
            channel_number=channel,
        )

        a.fade_in(1, overwrite=True)
        a.fade_out(1, overwrite=True)

        if channel < 4:
            a.bandpass_filter(2000, 6000, order=10, overwrite=True)
        else:
            a.highpass_filter(2000, order=10, overwrite=True)

        a.envelope(overwrite=True)
        a = normalization.noise_normalize(a, channel=sensor.channels[channel])

        # a.data.signal = robust_scale(a.data.signal)

        amplitude = (
            a.data.groupby(pd.Grouper(freq="s", key="datetime"))
            .max()
            .reset_index()["signal"]
            .to_list()
        )

        if "datetime" not in mo.columns:
            mo["datetime"] = pd.date_range(start=start, periods=length, freq="s")

        mo[f"channel_{channel}"] = amplitude

        if channel in internal_channels:
            mo[f"channel_{channel}_result"] = [
                1 if x > internal_cutoff else 0 for x in amplitude
            ]

        if channel in external_channels:
            mo[f"channel_{channel}_result"] = [
                1 if x > external_cutoff else 0 for x in amplitude
            ]

    mo["internal"] = mo[[f"channel_{i}_result" for i in internal_channels]].sum(axis=1)
    mo["external"] = mo[[f"channel_{i}_result" for i in external_channels]].sum(axis=1)
    mo["detection"] = mo.apply(
        lambda x: detection_algorithm(x["internal"], x["external"], 5), axis=1
    )

    return mo


def detection_display(db, sensor, start, duration, IT, NT, DR, NR):
    fig, axs = plt.subplots(
        ncols=1, nrows=6, sharex=True, figsize=(6, 5), height_ratios=[1, 1, 1, 1, 1, 1]
    )
    channels = [sensor.channels[i] for i in [0, 1, 2, 3, 7]]
    axs = axs.flatten()

    data = pd.DataFrame()

    for i, channel in enumerate(channels):
        ax = axs[i]
        a = db.get_audio(
            start=start,
            end=start + timedelta(seconds=duration),
            sensor=sensor,
            channel_number=channel.number,
        )

        a.fade_in(1, overwrite=True)
        a.fade_out(1, overwrite=True)

        if channel.number < 4:
            a.bandpass_filter(2000, 6000, order=10, overwrite=True)
        else:
            a.highpass_filter(2000, order=10, overwrite=True)

        a.envelope(overwrite=True)

        a = normalization.noise_normalize(a, channel=channel)

        # a.data.signal = robust_scale(a.data.signal)

        amplitude = (
            a.data.groupby(pd.Grouper(freq="s", key="datetime"))
            .max()
            .reset_index()["signal"][:-1]
        )
        
        ax.plot(a.data.seconds, a.data.signal, label=f"Ch. {channel.number}")

        ax.legend(loc="upper right", handlelength=0, handletextpad=0)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 50, 100])

        if channel.number < 4:
            # find indices where indices in list amplitude are greater than IT
            detections = amplitude[amplitude >= IT]
            for detection in detections.index:
                ax.axvspan(detection, detection + 1, color="red", alpha=0.3)

        else:
            detections = amplitude[amplitude >= NT]
            for detection in detections.index:
                ax.axvspan(detection, detection + 1, color="blue", alpha=0.3)

        data[f"channel_{channel.number}"] = [0] * 60
        data.loc[detections.index, f"channel_{channel.number}"] = 1
    data["internal"] = data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=1)
    data["external"] = data[[f"channel_{i}" for i in [7]]].sum(axis=1)
    data["detection"] = data.apply(
        lambda x: detection_algorithm(x["internal"], x["external"], 5), axis=1
    )
    data["classification"] = classification_algorithm(data["detection"], IT, NT, DR, NR)

    i_c = 0
    n_c = 0
    g_c = 0
    # axs[-1].plot([], [], label="Detection Display")
    for i, row in data.iterrows():
        if row["detection"] == "Insect":
            if i_c == 0:
                axs[-1].axvspan(i, i + 1, color="red", alpha=0.3, label="Insect")
                i_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
        elif row["detection"] == "Noise":
            if n_c == 0:
                axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3, label="Noise")
                n_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
        else:
            if g_c == 0:
                axs[-1].axvspan(i, i + 1, color="green", alpha=0.3, label="Clean")
                g_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)

    # remove the y-axis ticks from the last plot
    # add label to the legend for hte last plot
    # set the y-label for the last plot to say "Detection Display"
    axs[-1].set_yticks([])
    axs[-1].set_ylabel("Detection \n Display", fontsize=8)

    # set the transparency of the legend to 0.5
    axs[-1].legend(loc="upper right", ncols=4)

    # set figure x-axis label
    fig.supxlabel("Time [s]")
    fig.supylabel("Normalized Amplitude")

    return fig, axs


def nspa_detection_display(db, sensor, start, duration, IT, ET, DR, NR):
    fig, axs = plt.subplots(
        ncols=1, nrows=6, sharex=True, figsize=(6, 5), height_ratios=[1, 1, 1, 1, 1, 1]
    )
    channels = [sensor.channels[i] for i in [0, 1, 2, 3, 7]]
    axs = axs.flatten()

    data = pd.DataFrame()

    for i, channel in enumerate(channels):
        ax = axs[i]
        a = db.get_audio(
            start=start,
            end=start + timedelta(seconds=duration),
            sensor=sensor,
            channel_number=channel.number,
        )

        a.fade_in(1, overwrite=True)
        a.fade_out(1, overwrite=True)

        if channel.number < 4:
            a.bandpass_filter(2000, 6000, order=10, overwrite=True)
        else:
            a.highpass_filter(2000, order=10, overwrite=True)

        a.envelope(overwrite=True)

        a = normalization.noise_normalize(a, channel=channel)

        # a.data.signal = robust_scale(a.data.signal)

        amplitude = []
        for i, row in a.data.groupby(pd.Grouper(freq="s", key="datetime")):
            min_threshold = 0.5 * row["signal"].max()
            max_threshold = 0.9 * row["signal"].max()

            cutoff = row[row["signal"] >= min_threshold]
            cutoff = cutoff[cutoff["signal"] <= max_threshold]
            rms = np.sqrt(np.mean(cutoff["signal"] ** 2))
            amp = 20 * np.log10(rms)
            amplitude.append(amp)

        amplitude = pd.Series(amplitude)

        ax.plot(a.data.seconds, a.data.signal, label=f"Ch. {channel.number}")

        ax.legend(loc="upper right", handlelength=0, handletextpad=0)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 50, 100])

        if channel.number < 4:
            # find indices where indices in list amplitude are greater than IT
            detections = amplitude[amplitude >= IT]
            for detection in detections.index:
                ax.axvspan(detection, detection + 1, color="red", alpha=0.3)

        else:
            detections = amplitude[amplitude >= ET]
            for detection in detections.index:
                ax.axvspan(detection, detection + 1, color="blue", alpha=0.3)

        data[f"channel_{channel.number}"] = [0] * 60
        data.loc[detections.index, f"channel_{channel.number}"] = 1
    data["internal"] = data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=1)
    data["external"] = data[[f"channel_{i}" for i in [7]]].sum(axis=1)
    data["detection"] = data.apply(
        lambda x: detection_algorithm(x["internal"], x["external"], 5), axis=1
    )
    result = classification_algorithm(data["detection"], DR, NR)

    i_c = 0
    n_c = 0
    g_c = 0
    for i, row in data.iterrows():
        if row["detection"] == "Insect":
            if i_c == 0:
                axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
                i_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
        elif row["detection"] == "Noise":
            if n_c == 0:
                axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
                n_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
        else:
            if g_c == 0:
                axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)
                g_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)

    bold_font = FontProperties(weight="bold", family="Palatino Linotype")

    legend_handles = [
        Patch(color="red", alpha=1, label="Insect"),
        Patch(color="green", alpha=1, label="Clean"),
        Patch(color="blue", alpha=1, label="Noise"),
    ]

    legend = axs[-1].legend(handles=legend_handles, loc="upper right", ncols=4)

    for text in legend.get_texts():
        if text.get_text() == result:
            text.set_fontproperties(bold_font)
            text.set_text(r"\textbf{\underline{" + text.get_text() + "}}")

    # remove the y-axis ticks from the last plot
    # add label to the legend for hte last plot
    # set the y-label for the last plot to say "Detection Display"
    axs[-1].set_yticks([])
    axs[-1].set_ylabel("Detection \n Display", fontsize=8)

    # set the transparency of the legend to 0.5
    # axs[-1].legend(loc="upper right", ncols=4)

    # set figure x-axis label
    fig.supxlabel("Time [s]")
    fig.supylabel("Normalized Amplitude")

    return fig, axs


def cbts_detection_display(db, sensor, start, duration, IT, ET, DR, NR, internal_filt=[2000, 6000], external_filt=100, scaling_i=2, scaling_e = 2):
    fig, axs = plt.subplots(
        ncols=1, nrows=6, sharex=True, figsize=(6, 5), height_ratios=[1, 1, 1, 1, 1, 1]
    )
    channels = [sensor.channels[i] for i in [0, 1, 2, 3, 7]]
    axs = axs.flatten()

    data = pd.DataFrame()

    max_channel = None
    for i, channel in enumerate(channels):
        ax = axs[i]
        a = db.get_audio(
            start=start,
            end=start + timedelta(seconds=duration),
            sensor=sensor,
            channel_number=channel.number,
        )

        a.fade_in(1, overwrite=True)
        a.fade_out(1, overwrite=True)

        if channel.number < 4:
            a.bandpass_filter(internal_filt[0], internal_filt[1], order=10, overwrite=True)
        else:
            spl = acoustics.calculate_spl_dba(a.data.signal, a.sample_rate)
            spl = normalization.spl_coefficient(spl)
            
            a.highpass_filter(external_filt, order=10, overwrite=True)
            # a.bandpass_filter(2000, 6000, order=10, overwrite=True)

        a.envelope(overwrite=True)
        
        if channel.number < 4: 
            n = scaling_i * a.data.signal.median()
        else: 
            n = scaling_e * a.data.signal.median()
        # divide a by rms of n
        a.data.signal = a.data.signal / np.sqrt(np.mean(n**2))

        # a = normalization.noise_normalize(a, channel=channel)


        amplitude = []
        for i, row in a.data.groupby(pd.Grouper(freq="s", key="datetime")):
            amp = row.signal.max()
            amplitude.append(amp)

        amplitude = pd.Series(amplitude)

        if channel.number < 4:
            ax.plot(a.data.seconds, a.data.signal, label=f"Ch. {channel.number}")
        else:
            ax.plot(a.data.seconds, a.data.signal, label=f"Ch. {channel.number} - {round(spl,2)} [dBA]")

        ax.legend(loc="center right", handlelength=0, handletextpad=0, fontsize=8)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 20)
        ax.set_yticks([0, 10, 20])

        if channel.number < 4:
            # find indices where indices in list amplitude are greater than IT
            detections = amplitude[amplitude >= IT]
            for detection in detections.index:
                ax.axvspan(detection, detection + 1, color="red", alpha=0.3)

        else:
            detections = amplitude[amplitude >= ET]
            for detection in detections.index:
                ax.axvspan(detection, detection + 1, color="blue", alpha=0.3)

        data[f"channel_{channel.number}"] = [0] * 60
        data.loc[detections.index, f"channel_{channel.number}"] = 1
    data["internal"] = data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=1)
    data["external"] = data[[f"channel_{i}" for i in [7]]].sum(axis=1)
    # find which column (channel_{i}) has the maximum sum
    max_channel = int(data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=0).idxmax().split("_")[-1])
    ax[max_channel]

    data["detection"] = data.apply(
        lambda x: detection_algorithm(x["internal"], x["external"], 5), axis=1
    )
    result = classification_algorithm(data["detection"], DR, NR)

    i_c = 0
    n_c = 0
    g_c = 0
    for i, row in data.iterrows():
        if row["detection"] == "Insect":
            if i_c == 0:
                axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
                i_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
        elif row["detection"] == "Noise":
            if n_c == 0:
                axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
                n_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
        else:
            if g_c == 0:
                axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)
                g_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)

    bold_font = FontProperties(weight="bold", family="Palatino Linotype")

    legend_handles = [
        Patch(color="red", alpha=1, label="Insect"),
        Patch(color="green", alpha=1, label="Clean"),
        Patch(color="blue", alpha=1, label="Noise"),
    ]

    legend = axs[-1].legend(handles=legend_handles, loc="center right", ncols=4, fontsize=8)

    for text in legend.get_texts():
        if text.get_text() == result:
            text.set_fontproperties(bold_font)
            text.set_text(r"\textbf{\underline{" + text.get_text() + "}}")
            text.set_fontsize(8)

    # remove the y-axis ticks from the last plot
    # add label to the legend for hte last plot
    # set the y-label for the last plot to say "Detection Display"
    axs[-1].set_yticks([])
    axs[-1].set_ylabel("Detection \n Display", fontsize=8)

    # set the transparency of the legend to 0.5
    # axs[-1].legend(loc="upper right", ncols=4)

    # set figure x-axis label
    fig.supxlabel("Time [s]", fontsize=10)
    fig.supylabel("Normalized Amplitude", fontsize=10)

    return fig, axs


def spectral_subtraction_display(db, sensor, start, duration, IT, ET, DR, NR, **kwargs):
    fig, axs = plt.subplots(
        ncols=1, nrows=6, sharex=True, figsize=(6, 5), height_ratios=[1, 1, 1, 1, 1, 1]
    )
    channels = [sensor.channels[i] for i in [0, 1, 2, 3, 7]]
    axs = axs.flatten()

    data = pd.DataFrame()

    # check kwargs for filter parameters
    if "internal_low_cutoff" in kwargs:
        internal_low_cutoff = kwargs["internal_low_cutoff"]
    else:
        internal_low_cutoff = 2000
    
    if "internal_high_cutoff" in kwargs:
        internal_high_cutoff = kwargs["internal_high_cutoff"]
    else:
        internal_high_cutoff = 6000

    external = db.get_audio(
        start=start,
        end=start + timedelta(seconds=duration),
        sensor=sensor,
        channel_number=7,
    )

    for i, channel in enumerate(channels):
        ax = axs[i]
        a = db.get_audio(
            start=start,
            end=start + timedelta(seconds=duration),
            sensor=sensor,
            channel_number=channel.number,
        )

        a.fade_in(1, overwrite=True)
        a.fade_out(1, overwrite=True)

        if channel.number < 4:
            a.data.signal = audio.spectral_subtraction(
                a.data.signal, external.data.signal, 1
            )
            a.bandpass_filter(internal_low_cutoff, internal_high_cutoff, order=10, overwrite=True)
        else:
            a.highpass_filter(100, order=10, overwrite=True)
            # a.bandpass_filter(2000, 6000, order=10, overwrite=True)

        a.envelope(overwrite=True)

        n = 2 * a.data.signal.median()
        # divide a by rms of n
        a.data.signal = a.data.signal / np.sqrt(np.mean(n**2))

        # a = normalization.noise_normalize(a, channel=channel)

        amplitude = []
        for i, row in a.data.groupby(pd.Grouper(freq="s", key="datetime")):
            amp = row.signal.max()
            amplitude.append(amp)

        amplitude = pd.Series(amplitude)

        ax.plot(a.data.seconds, a.data.signal, label=f"Ch. {channel.number}")

        ax.legend(loc="upper right", handlelength=0, handletextpad=0)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 20)
        ax.set_yticks([0, 10, 20])

        if channel.number < 4:
            # find indices where indices in list amplitude are greater than IT
            detections = amplitude[amplitude >= IT]
            for detection in detections.index:
                ax.axvspan(detection, detection + 1, color="red", alpha=0.3)

        else:
            detections = amplitude[amplitude >= ET]
            for detection in detections.index:
                ax.axvspan(detection, detection + 1, color="blue", alpha=0.3)

        data[f"channel_{channel.number}"] = [0] * 60
        data.loc[detections.index, f"channel_{channel.number}"] = 1
    data["internal"] = data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=1)
    data["external"] = data[[f"channel_{i}" for i in [7]]].sum(axis=1)
    data["detection"] = data.apply(
        lambda x: detection_algorithm(x["internal"], x["external"], 5), axis=1
    )
    result = classification_algorithm(data["detection"], DR, NR)

    i_c = 0
    n_c = 0
    g_c = 0
    for i, row in data.iterrows():
        if row["detection"] == "Insect":
            if i_c == 0:
                axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
                i_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
        elif row["detection"] == "Noise":
            if n_c == 0:
                axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
                n_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
        else:
            if g_c == 0:
                axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)
                g_c = 1
            else:
                axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)

    bold_font = FontProperties(weight="bold", family="Palatino Linotype")

    legend_handles = [
        Patch(color="red", alpha=1, label="Insect"),
        Patch(color="green", alpha=1, label="Clean"),
        Patch(color="blue", alpha=1, label="Noise"),
    ]

    legend = axs[-1].legend(handles=legend_handles, loc="upper right", ncols=4)

    for text in legend.get_texts():
        if text.get_text() == result:
            text.set_fontproperties(bold_font)
            text.set_text(r"\textbf{\underline{" + text.get_text() + "}}")

    # remove the y-axis ticks from the last plot
    # add label to the legend for hte last plot
    # set the y-label for the last plot to say "Detection Display"
    axs[-1].set_yticks([])
    axs[-1].set_ylabel("Detection \n Display", fontsize=8)

    # set the transparency of the legend to 0.5
    # axs[-1].legend(loc="upper right", ncols=4)

    # set figure x-axis label
    fig.supxlabel("Time [s]")
    fig.supylabel("Normalized Amplitude")

    return fig, axs

def cbts_detection(db, sensor, start, duration, IT, ET, DR, NR, internal_filt=[2000, 6000], external_filt=100, scaling_i=2, scaling_e = 2):
    channels = [sensor.channels[i] for i in [0, 1, 2, 3, 7]]

    data = pd.DataFrame()
    internal_signals = []


    for i, channel in enumerate(channels):
        a = db.get_audio(
            start=start,
            end=start + timedelta(seconds=duration),
            sensor=sensor,
            channel_number=channel.number,
        )

        a.fade_in(1, overwrite=True)
        a.fade_out(1, overwrite=True)

        if channel.number < 4:
            a.bandpass_filter(internal_filt[0], internal_filt[1], order=10, overwrite=True)
        else:
            spl = acoustics.calculate_spl_dba(a.data.signal, a.sample_rate)
            spl = normalization.calculate_spl_dba(spl)

            a.highpass_filter(external_filt, order=10, overwrite=True)
            # a.bandpass_filter(2000, 6000, order=10, overwrite=True)

        a.envelope(overwrite=True)
        
        if channel.number < 4: 
            n = scaling_i * a.data.signal.median()
        else: 
            n = scaling_e * a.data.signal.median()
        # divide a by rms of n
        a.data.signal = a.data.signal / np.sqrt(np.mean(n**2))

        amplitude = []
        for i, row in a.data.groupby(pd.Grouper(freq="s", key="datetime")):
            amp = row.signal.max()
            amplitude.append(amp)

        amplitude = pd.Series(amplitude)

        if channel.number < 4:
            internal_signals.append(amplitude)  # Collect internal channel signals


        data[f"channel_{channel.number}"] = [0] * 60
        data.loc[amplitude.index, f"channel_{channel.number}"] = amplitude

        if channel.number < 4:
            # find indices where indices in list amplitude are greater than IT
            detections = amplitude[amplitude >= IT]
        else:
            detections = amplitude[amplitude >= ET]
        
        data[f"channel_{channel.number}"] = [0] * 60
        data.loc[detections.index, f"channel_{channel.number}"] = 1

    data["internal"] = data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=1)
    data["external"] = data[[f"channel_{i}" for i in [7]]].sum(axis=1)
    data["detection"] = data.apply(
        lambda x: detection_algorithm(x["internal"], x["external"], 5), axis=1
    )

    # Analyze internal signals for uniformity
    internal_signals_df = pd.DataFrame(internal_signals).T
    internal_max_channel = internal_signals_df.idxmax(axis=1)  # Channel with strongest signal
    internal_std = internal_signals_df.std(axis=1)  # Standard deviation across channels

    # Determine if signals are likely caused by external noise
    external_noise_flag = (internal_std < 1).all()  # Example threshold for uniformity

    # Count detections
    internal = data[data["internal"] > 0].shape[0]
    external = data[data["external"] > 0].shape[0]

    result = classification_algorithm(data["detection"], DR, NR)

    if external_noise_flag:
        result = "Noise"

    # find the channel with the most detections
    internal_max_channel = internal_max_channel.value_counts().index[0]

    return internal, external, result, internal_max_channel