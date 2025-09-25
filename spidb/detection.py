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
import copy

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

def retreive_acoustic_data(db, sensor, start, end=None, channels=[0, 1, 2, 3, 7], duration=60):
    
    data = []

    channels = [sensor.channels[i] for i in channels]
    for channel in channels:
        a = db.get_audio(
            start=start,
            end=start + timedelta(seconds=duration),
            sensor=sensor,
            channel_number=channel.number,
        )
        data.append(a)

    return data

def acoustic_detection(
    channels,
    IT=5,
    ET=5,
    DR=30,  
    NR=30,
    internal_filt=[1625, 5400],
    external_filt=[1625, 5400],
    scaling_i=2,
    scaling_e=2,
    return_audio=False,
    db=None,
):
    data = pd.DataFrame()
    internal_signals = []

    # create a copy of the channels list to avoid modifying the original list
    channels = [copy.deepcopy(channel) for channel in channels]

    audio_data = pd.DataFrame()

    for i, a in enumerate(channels):
        a.fade_in(1, overwrite=True)
        a.fade_out(1, overwrite=True)

        if a.channel_number < 4:
            a.bandpass_filter(
                internal_filt[0], internal_filt[1], order=10, overwrite=True
            )
        else:
            spl = normalization.calculate_spl(a.data.signal) #.calculate_spl_dba(a.data.signal, a.sample_rate)
            spl = normalization.spl_coefficient(spl)
            if isinstance(external_filt, (int, float)):
                a.highpass_filter(external_filt, order=10, overwrite=True)
            else:
                a.bandpass_filter(
                    external_filt[0], external_filt[1], order=10, overwrite=True
                )
        a.envelope(overwrite=True)

        if a.channel_number < 4:
            n = scaling_i * a.data.signal.median()
        else:
            n = scaling_e * a.data.signal.median()
        # divide a by rms of n
        a.data.signal = a.data.signal / np.sqrt(np.mean(n**2))


        # if a.channel_number < 4:
        # channel = db.session.get(spidb.Sensor, 1).channels[a.channel_number]

        # a = normalization.noise_normalize(db, a, channel=channel, filter="bandpass", low=internal_filt[0], high=internal_filt[1], coefficient="set")
        # else:
        #     a = normalization.noise_normalize(a, channel=a.channel_number, filter="highpass", low=external_filt if isinstance(external_filt, (int, float)) else external_filt[0], coefficient="set")

        # coef =  normalization.noise_coefficient(db, channel.sensor, channel, "bandpass", internal_filt[0], internal_filt[1], order=10)

        # a.data.signal = a.data.signal / coef

        amplitude = []
        for i, row in a.data.groupby(pd.Grouper(freq="s", key="datetime")):
            amp = row.signal.max()
            amplitude.append(amp)

        amplitude = pd.Series(amplitude)

        if a.channel_number < 4:
            internal_signals.append(amplitude)  # Collect internal channel signals

        data[f"channel_{a.channel_number}"] = np.zeros(60, dtype=float)
        data.loc[amplitude.index, f"channel_{a.channel_number}"] = amplitude

        if a.channel_number < 4:
            # find indices where indices in list amplitude are greater than IT
            detections = amplitude[amplitude >= IT]
        else:
            detections = amplitude[amplitude >= ET]

        data[f"channel_{a.channel_number}"] = np.zeros(60, dtype=int)
        data.loc[detections.index, f"channel_{a.channel_number}"] = 1

        if "datetime" not in audio_data.columns:
            audio_data["datetime"] = a.data.datetime
        if "seconds" not in audio_data.columns:
            audio_data["seconds"] = a.data.seconds
            
        audio_data[f"channel_{a.channel_number}"] = a.data.signal

    data["internal"] = data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=1)
    data["external"] = data[[f"channel_{i}" for i in [7]]].sum(axis=1)
    data["detection"] = data.apply(
        lambda x: detection_algorithm(x["internal"], x["external"], 5), axis=1
    )

    # Analyze internal signals for uniformity
    internal_signals_df = pd.DataFrame(internal_signals).T
    internal_max_channel = internal_signals_df.idxmax(
        axis=1
    )  # Channel with strongest signal
    # internal_std = internal_signals_df.std(axis=1)  # Standard deviation across channels

    # Determine if signals are likely caused by external noise
    # external_noise_flag = (internal_std < 1).all()  # Example threshold for uniformity

    # Count detections
    internal = data[data["internal"] > 0].shape[0]
    external = data[data["external"] > 0].shape[0]

    result = classification_algorithm(data["detection"], DR, NR)

    # if external_noise_flag:
        # result = "Noise"

    # find the channel with the most detections
    internal_max_channel = int(internal_max_channel.value_counts().index[0])

    data.attrs["result"] = result
    data.attrs["internal_max_channel"] = internal_max_channel
    data.attrs["internal"] = internal
    data.attrs["external"] = external
    data.attrs["external_spl"] = float(spl)

    if return_audio:
        return data, audio_data
    else: 
        return data

def acoustic_detection_display(
   data, audio_data, time_format="datetime", legend="center right", spl=True, latex=True
):
    fig, axs = plt.subplots(
        ncols=1, nrows=6, sharex=True, figsize=(6, 3.5), height_ratios=[1, 1, 1, 1, 1, 1]
    )
    # get list of columns that contain "channel_"
    channels = [col for col in data.columns if col.startswith("channel_")]

    bold_font = FontProperties(weight="bold")
    
    for i, channel in enumerate(channels):
        ch = int(channel.split("_")[-1])
        label = f"Piezoelectric - Ch. {ch}"
        if data.attrs["result"] == "Insect" and data.attrs["internal_max_channel"] == ch:
            # make the label bold and underlined
            if latex:
                label = r"\textbf{\underline{" + str(label) + "}}"
            else:
                # make the label bold and underlined with the bold_font property
                label = f"{label} (max)"

        if ch == 7:
            if spl:
                label = f"Microphone - Ch. {ch} ({round(data.attrs['external_spl'], 2)} dBA)"
            else:
                label = f"Microphone - Ch. {ch}"
        ax = axs[i]
        if time_format == "datetime":
            ax.plot(
                audio_data["datetime"],
                audio_data[channel],
                label=label,
            )
        else:
            ax.plot(audio_data["seconds"], audio_data[channel], label=label)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 50, 100])
        ax.legend(loc=legend, handlelength=0, handletextpad=0)

        # Highlight detections
        detections = data[data[channel] == 1].index
        for detection in detections:
            if ch < 4:
                ax.axvspan(detection, detection + 1, color="red", alpha=0.3)
            else:
                ax.axvspan(detection, detection + 1, color="blue", alpha=0.3)            

    for i, row in data.iterrows(): 
        if row["detection"] == "Insect":
            axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
        elif row["detection"] == "Noise":
            axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
        else:
            axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)

    # TODO update font


    legend_handles = [
        Patch(color="red", alpha=1, label="Insect"),
        Patch(color="green", alpha=1, label="Clean"),
        Patch(color="blue", alpha=1, label="Noise"),
    ]

    legend = axs[-1].legend(
        handles=legend_handles, loc=legend, ncols=3
    )

    for text in legend.get_texts():
        if text.get_text() == data.attrs["result"]:
            if latex: 
                text.set_fontproperties(bold_font)
                text.set_text(r"\textbf{\underline{" + text.get_text() + "}}")
            else:
                text.set_fontproperties(bold_font)
                text.set_text(f"{text.get_text()}")
            # text.set_fontsize(10)

    axs[-1].set_yticks([])
    axs[-1].set_ylabel("Detection \n Display", fontsize=10)

    # # set the transparency of the legend to 0.5
    # # axs[-1].legend(loc="upper right", ncols=4)

    # # set figure x-axis label
    fig.supxlabel("Time [s]")
    fig.supylabel("Normalized Amplitude")

    return fig, axs
    # channels = [sensor.channels[i] for i in [0, 1, 2, 3, 7]]
    # axs = axs.flatten()

    # data = pd.DataFrame()

    # max_channel = None
    # for i, channel in enumerate(channels):
    #     ax = axs[i]
    #     a = db.get_audio(
    #         start=start,
    #         end=start + timedelta(seconds=duration),
    #         sensor=sensor,
    #         channel_number=channel.channel_number,
    #     )

    #     a.fade_in(1, overwrite=True)
    #     a.fade_out(1, overwrite=True)

    #     if channel.channel_number < 4:
    #         a.bandpass_filter(
    #             internal_filt[0], internal_filt[1], order=10, overwrite=True
    #         )
    #     else:
    #         spl = acoustics.calculate_spl_dba(a.data.signal, a.sample_rate)
    #         spl = normalization.spl_coefficient(spl)

    #         a.highpass_filter(external_filt, order=10, overwrite=True)
    #         # a.bandpass_filter(2000, 6000, order=10, overwrite=True)

    #     a.envelope(overwrite=True)

    #     if channel.channel_number < 4:
    #         n = scaling_i * a.data.signal.median()
    #     else:
    #         n = scaling_e * a.data.signal.median()
    #     # divide a by rms of n
    #     a.data.signal = a.data.signal / np.sqrt(np.mean(n**2))

    #     # a = normalization.noise_normalize(a, channel=channel)

    #     amplitude = []
    #     for i, row in a.data.groupby(pd.Grouper(freq="s", key="datetime")):
    #         amp = row.signal.max()
    #         amplitude.append(amp)

    #     amplitude = pd.Series(amplitude)

    #     if channel.channel_number < 4:
    #         ax.plot(a.data.seconds, a.data.signal, label=f"Ch. {channel.channel_number}")
    #     else:
    #         ax.plot(
    #             a.data.seconds,
    #             a.data.signal,
    #             label=f"Ch. {channel.channel_number} - {round(spl, 2)} [dBA]",
    #         )

    #     ax.legend(loc="center right", handlelength=0, handletextpad=0, fontsize=8)
    #     ax.set_xlim(0, 60)
    #     ax.set_ylim(0, 20)
    #     ax.set_yticks([0, 10, 20])

    #     if channel.channel_number < 4:
    #         # find indices where indices in list amplitude are greater than IT
    #         detections = amplitude[amplitude >= IT]
    #         for detection in detections.index:
    #             ax.axvspan(detection, detection + 1, color="red", alpha=0.3)

    #     else:
    #         detections = amplitude[amplitude >= ET]
    #         for detection in detections.index:
    #             ax.axvspan(detection, detection + 1, color="blue", alpha=0.3)

    #     data[f"channel_{channel.channel_number}"] = [0] * 60
    #     data.loc[detections.index, f"channel_{channel.channel_number}"] = 1
    # data["internal"] = data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=1)
    # data["external"] = data[[f"channel_{i}" for i in [7]]].sum(axis=1)
    # # find which column (channel_{i}) has the maximum sum
    # max_channel = int(
    #     data[[f"channel_{i}" for i in [0, 1, 2, 3]]].sum(axis=0).idxmax().split("_")[-1]
    # )
    # ax[max_channel]

    # data["detection"] = data.apply(
    #     lambda x: detection_algorithm(x["internal"], x["external"], 5), axis=1
    # )
    # result = classification_algorithm(data["detection"], DR, NR)

    # i_c = 0
    # n_c = 0
    # g_c = 0
    # for i, row in data.iterrows():
    #     if row["detection"] == "Insect":
    #         if i_c == 0:
    #             axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
    #             i_c = 1
    #         else:
    #             axs[-1].axvspan(i, i + 1, color="red", alpha=0.3)
    #     elif row["detection"] == "Noise":
    #         if n_c == 0:
    #             axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
    #             n_c = 1
    #         else:
    #             axs[-1].axvspan(i, i + 1, color="blue", alpha=0.3)
    #     else:
    #         if g_c == 0:
    #             axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)
    #             g_c = 1
    #         else:
    #             axs[-1].axvspan(i, i + 1, color="green", alpha=0.3)

    # bold_font = FontProperties(weight="bold", family="Palatino Linotype")

    # legend_handles = [
    #     Patch(color="red", alpha=1, label="Insect"),
    #     Patch(color="green", alpha=1, label="Clean"),
    #     Patch(color="blue", alpha=1, label="Noise"),
    # ]

    # legend = axs[-1].legend(
    #     handles=legend_handles, loc="center right", ncols=4, fontsize=8
    # )

    # for text in legend.get_texts():
    #     if text.get_text() == result:
    #         text.set_fontproperties(bold_font)
    #         text.set_text(r"\textbf{\underline{" + text.get_text() + "}}")
    #         text.set_fontsize(8)

    # # remove the y-axis ticks from the last plot
    # # add label to the legend for hte last plot
    # # set the y-label for the last plot to say "Detection Display"
    # axs[-1].set_yticks([])
    # axs[-1].set_ylabel("Detection \n Display", fontsize=8)

    # # set the transparency of the legend to 0.5
    # # axs[-1].legend(loc="upper right", ncols=4)

    # # set figure x-axis label
    # fig.supxlabel("Time [s]", fontsize=10)
    # fig.supylabel("Normalized Amplitude", fontsize=10)

    # return fig, axs
# %%