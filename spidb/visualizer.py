# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import signal
from dankpy import colors
from matplotlib.patches import Rectangle
from tsdownsample import MinMaxLTTBDownsampler


# %%
def waveform_display(
    db,
    start,
    end,
    sensor,
    time_format="datetime",
    normalize=True,
    compressed=False,
    envelope=False,
    filter=False,
):
    if compressed:
        fig, axs = plt.subplots(
            nrows=4,
            ncols=2,
            sharex=True,
            layout="compressed",
            figsize=(3, 4),
        )

        axs = axs.flatten(order="F")
    else:
        fig, axs = plt.subplots(
            nrows=8,
            ncols=1,
            sharex=True,
            layout="compressed",
            figsize=(1.5 * 6, 1.5 * 6),
        )
    # fig, axs = plt.subplots(nrows=8, ncols=1, sharex=True, layout="compressed")
    channels = np.arange(0, 8).tolist()

    for c in channels:
        a = db.get_audio(start, end, channel=c, sensor=sensor)

        ax = axs[c]

        if filter:
            if sensor == "ASPIDS":
                if c < 4:
                    a.bandpass_filter(500, 6000, order=10, overwrite=True)
                else:
                    a.highpass_filter(500, order=10, overwrite=True)
            else:
                if c < 6:
                    a.lowpass_filter(100, order=10, overwrite=True)
                else:
                    a.highpass_filter(500, order=10, overwrite=True)

        if envelope:
            a.envelope(overwrite=True)

        if normalize:
            if sensor == "ASPIDS":
                level = np.median(a.data.signal)
                noise = a.data.signal[a.data.signal < level]
                a.data.signal = a.data.signal / np.sqrt(np.mean(noise**2))

            if sensor == "MSPIDS":
                if c < 6:
                    a.data.signal = a.data.signal / 0.1 * a.data.signal.max()
                else:
                    level = np.median(a.data.signal)
                    noise = a.data.signal[a.data.signal < level]
                    a.data.signal = a.data.signal / np.sqrt(np.mean(noise**2))

        if sensor == "ASPIDS":
            if c < 4:
                ax.set_title(f"Ch. {c} - Piezoelectric")
                ax.set_ylim(0, 500)
                ax.set_yticks([0, 250, 500])
            else:
                ax.set_title(f"Ch. {c} - Microphone")
                ax.set_ylim(0, 100)
                ax.set_yticks([0, 50, 100])
        else:
            if c < 6:
                ax.set_title(f"Ch. {c} - Microwave")
                ax.set_ylim(0, 5)
            elif c == 6:
                ax.set_title(f"Ch. {c} - Microphone")
                ax.set_ylim(0, 100)
                ax.set_yticks([0, 50, 100])
            else:
                ax.set_title(f"Ch. {c} - Piezoelectric")
                ax.set_ylim(0, 100)
                ax.set_yticks([0, 50, 100])

        ax.yaxis.set_label_position("right")

        if time_format == "datetime":
            ax.plot(a.data.datetime, a.data.signal)
            ax.xaxis.set_ticks(np.arange(a.data.datetime.min(), a.data.datetime.max()))

            myFmt = mdates.DateFormatter("%H:%M:%S")
            ax.xaxis.set_major_formatter(myFmt)
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))

        elif time_format == "seconds":
            ax.plot(a.data["time [s]"], a.data.signal)
            ax.set_xlim(
                [round(a.data["time [s]"].min()), round(a.data["time [s]"].max())]
            )

        if envelope and normalize and filter:
            ax.set_ylim(0, None)

    if time_format == "datetime":
        fig.supxlabel(f"Time on {a.data.datetime.iloc[0].date()}")
    else:
        fig.supxlabel("Time [s]")

    if normalize:
        fig.supylabel("Normalized Amplitude")
    else:
        fig.supylabel("Amplitude")

    return fig, axs


def spectrogram_display(
    db,
    start,
    end,
    sensor,
    time_format="datetime",
    section="all",
    showscale=False,
    zmin=None,
    zmax=None,
    compressed=False,
):
    if zmin is None and zmax is None:
        if sensor == "ASPIDS":
            zmin = -140
            zmax = -80
        else:
            zmin = -100
            zmax = -50

    if section == "internal":
        if sensor == "ASPIDS":
            fig, axs = plt.subplots(
                nrows=4,
                ncols=1,
                sharex=True,
                layout="compressed",
                figsize=(5.6, (5.6 / 1.6180) * (2 / 2)),
            )  # mdpi
            # fig, axs = plt.subplots(nrows=4, ncols=1, sharex=True, layout="compressed", figsize=(1.5*3, 1.5*3))

            channels = np.arange(0, 4).tolist()

            for c in channels:
                ax = axs[c]
                a = db.get_audio(start, end, channel=c, sensor=sensor)

                if time_format == "datetime":
                    times, frequencies, spectrogram = a.spectrogram(
                        window="hann",
                        window_size=1024,
                        nperseg=1024,
                        nfft=1024,
                        noverlap=512,
                        time_format="datetime",
                    )
                elif time_format == "seconds":
                    times, frequencies, spectrogram = a.spectrogram(
                        window="hann",
                        window_size=1024,
                        nperseg=1024,
                        nfft=1024,
                        noverlap=512,
                        time_format="seconds",
                    )
                spectrogram = 10 * np.log10(np.abs(spectrogram))
                extents = [
                    times.min(),
                    times.max(),
                    frequencies.min(),
                    frequencies.max(),
                ]
                axi = ax.imshow(
                    spectrogram,
                    extent=extents,
                    cmap="jet",
                    aspect="auto",
                    origin="lower",
                )
                axi.set_clim([zmin, zmax])
                ax.set_ylabel(f"Ch. {c}")
                ax.yaxis.set_label_position("right")
                # ax.get_yaxis().set_label_coords(1.015, 0.6)
    elif section == "external":
        if sensor == "ASPIDS":
            fig, axs = plt.subplots(
                nrows=4,
                ncols=1,
                sharex=True,
                layout="compressed",
                figsize=(5.6, (5.6 / 1.6180) * (2 / 2)),
            )

            channels = np.arange(4, 8).tolist()

            for c in channels:
                ax = axs[c - 4]
                a = db.get_audio(start, end, channel=c, sensor=sensor)

                if time_format == "datetime":
                    times, frequencies, spectrogram = a.spectrogram(
                        window="hann",
                        window_size=1024,
                        nperseg=1024,
                        nfft=1024,
                        noverlap=512,
                        time_format="datetime",
                    )
                elif time_format == "seconds":
                    times, frequencies, spectrogram = a.spectrogram(
                        window="hann",
                        window_size=1024,
                        nperseg=1024,
                        nfft=1024,
                        noverlap=512,
                        time_format="seconds",
                    )
                spectrogram = 10 * np.log10(np.abs(spectrogram))
                extents = [
                    times.min(),
                    times.max(),
                    frequencies.min(),
                    frequencies.max(),
                ]
                axi = ax.imshow(
                    spectrogram,
                    extent=extents,
                    cmap="jet",
                    aspect="auto",
                    origin="lower",
                )

                axi.set_clim([zmin, zmax])
                ax.set_ylabel(f"Ch. {c}")
                ax.yaxis.set_label_position("right")

    else:
        if compressed:
            if sensor == "ASPIDS":
                fig, axs = plt.subplots(
                    nrows=4,
                    ncols=2,
                    sharex=True,
                    sharey=True,
                    layout="compressed",
                    figsize=(3, 4),
                )
            else:
                fig, axs = plt.subplots(
                    nrows=4,
                    ncols=2,
                    sharex=True,
                    layout="compressed",
                    figsize=(3, 4),
                )

            axs = axs.flatten(order="F")

        else:
            fig, axs = plt.subplots(
                nrows=8, ncols=1, sharex=True, layout="compressed", figsize=(5.6, 3.5)
            )

        channels = np.arange(0, 8).tolist()

        for c in channels:
            a = db.get_audio(start, end, channel=c, sensor=sensor)

            if time_format == "datetime":
                times, frequencies, spectrogram = a.spectrogram(
                    window="hann",
                    window_size=1024,
                    nperseg=1024,
                    nfft=1024,
                    noverlap=512,
                    time_format="datetime",
                )

            elif time_format == "seconds":
                times, frequencies, spectrogram = a.spectrogram(
                    window="hann",
                    window_size=1024,
                    nperseg=1024,
                    nfft=1024,
                    noverlap=512,
                    time_format="seconds",
                )
            spectrogram = 10 * np.log10(np.abs(spectrogram))

            extents = [times.min(), times.max(), frequencies.min(), frequencies.max()]

            ax = axs[c]

            axi = ax.imshow(
                spectrogram,
                extent=extents,
                cmap="jet",
                aspect="auto",
                origin="lower",
            )
            axi.set_clim([zmin, zmax])
            ax.yaxis.set_label_position("right")

            if sensor == "ASPIDS":
                fig.sharey = True
                ax.set_ylim(0, 8000)
                ax.set_yticks([0, 4000, 8000])
                # if c < 4:
                #     ax.set_ylabel(f"Ch. {c} - Piezo.")
                # if c > 3:
                #     ax.set_ylabel(f"Ch. {c} - Mic.")
            else:
                if c < 6:
                    # ax.set_ylabel(f"Ch. {c} - Micro.")
                    ax.set_ylim(0, 200)
                    ax.set_yticks([0, 100, 200])
                elif c == 6:
                    # ax.set_ylabel(f"Ch. {c} - Mic.")
                    ax.set_ylim(0, 2000)
                    ax.set_yticks([0, 1000, 2000])
                else:
                    # ax.set_ylabel(f"Ch. {c} - Piezo.")
                    ax.set_ylim(0, 2000)
                    ax.set_yticks([0, 1000, 2000])

            if sensor == "ASPIDS":
                if c < 4:
                    ax.set_title(f"Ch. {c} - Piezoelectric")
                else:
                    ax.set_title(f"Ch. {c} - Microphone")
            else:
                if c < 6:
                    ax.set_title(f"Ch. {c} - Microwave")
                elif c == 6:
                    ax.set_title(f"Ch. {c} - Microphone.")
                else:
                    ax.set_title(f"Ch. {c} - Piezoelectric")

            ax.yaxis.set_label_position("right")
    if time_format == "datetime":
        ax.set_xlim([times.min(), times.max()])
        myFmt = mdates.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(myFmt)

    else:
        ax.set_xlim([round(times.min()), round(times.max())])
        ax.set_xlim([round(times.min()), round(times.max())])

    if time_format == "datetime":
        fig.supxlabel(f"Time on {a.data.datetime[0].date()}")
    else:
        fig.supxlabel("Time [s]")

    if showscale:
        if compressed:
            cbar = fig.colorbar(
                axi, ax=axs.ravel().tolist(), orientation="horizontal", location="top"
            )
            cbar.ax.set_title("Power [dB]")
        else:
            cbar = fig.colorbar(
                axi, ax=axs.ravel().tolist(), orientation="vertical", location="right"
            )
            cbar.ax.set_ylabel("Power [dB]")
    fig.supylabel("Frequency [Hz]")

    return fig, axs


def spectra_display(db, start, end, sensor, section="all", spl=False):
    fig, ax = plt.subplots()

    # if section == "internal":


    #     for c in channels:
    #         a = db.get_audio(start, end, channel=c, sensor=sensor)

    #         a.fade_in(fade_time=2, overwrite=True)
    #         a.fade_out(fade_time=2, overwrite=True)

    #         f, p = signal.welch(
    #             a.data.signal,
    #             fs=a.sample_rate,
    #             nperseg=1024,
    #             window="blackmanharris",
    #             average="mean",
    #             scaling="spectrum",
    #         )

    #         ax.plot(f, 10 * np.log10(p), label=f"Ch. {c}", color=colors[c])

    if section == "all":
        channels = np.arange(0, 8).tolist()
    elif section == "internal":
        if sensor == "ASPIDS":
            channels = np.arange(0, 4).tolist()
        else:
            channels = np.arange(0, 6).tolist()
    elif isinstance(section, list):
        channels = section

    for i, c in enumerate(channels):
        a = db.get_audio(start, end, channel=c, sensor=sensor)

        a.fade_in(fade_time=2, overwrite=True)
        a.fade_out(fade_time=2, overwrite=True)

        f, p = signal.welch(
            a.data.signal,
            fs=a.sample_rate,
            nperseg=1024,
            nfft=1024,
            noverlap=512,
            window="blackmanharris",
            average="mean",
            scaling="spectrum",
        )

        if sensor == "ASPIDS":
            if section == "internal": 
                color = colors[i]
            else: 
                if c < 4:
                    color = "black"
                else:
                    color = "red"
        else:
            if c < 6:
                color = "black"
            else:
                color = "red"

        p = 10 *np.log10(p)
        if spl: 
            p_f = p[(f >= 500) & (f <= 6000)]
            pl = 10 * np.log10(np.sum(10 ** (p_f / 10)))
            ax.plot(f, p, label=f"Ch. {c} ({round(pl)} SPL)", c=color)
        else: 
            ax.plot(f, p, label=f"Ch. {c}", c=color)

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("PSD [dB]")
    ax.legend(loc="upper right", ncols=len(channels))

    # if len(channels) < 4: 
    #     ax.legend(loc="upper right", ncols=2)
    # else: 

    return fig, ax

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

    if sensor == "ASPIDS":
        fig, axs = plt.subplots(
            nrows=6,
            ncols=1,
            sharex=True,
            # layout="compressed",
            figsize=(5.6, 4.15),
        )  # mdpi
    if sensor == "MSPIDS":
        fig, axs = plt.subplots(
            nrows=7,
            ncols=1,
            sharex=True,
            layout="compressed",
            figsize=(5.6, (5.6 / 1.6180) * (4 / 2)),
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
            ax.plot(data["time [s]"].values[s_ds], row.values[s_ds])
            eligble = mo[mo[row.name] == 1]["time [s]"]
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

    if sensor == "ASPIDS":
        ax = axs[i + 1]
        row = external.iloc[:, 3]
        s_ds = MinMaxLTTBDownsampler().downsample(data["datetime"], row, n_out=1000)
        if time_format == "datetime":
            ax.plot(data["datetime"][s_ds], row[s_ds])
            eligble = mo[mo[row.name] == 1].datetime
            width = 1.1574074074074075e-05
        else:
            ax.plot(data["time [s]"][s_ds], row[s_ds])
            eligble = mo[mo[row.name] == 1]["time [s]"]
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
            ax.set_xlim([min(data["time [s]"]), round(max(data["time [s]"]))])

    # for i in range(len(data)):
    #     ax = axs[i]
    #     row = data[i]

    #     s_ds = MinMaxLTTBDownsampler().downsample(row["datetime"], row["signal"], n_out = 1000)

    #     if method == "datetime":
    #         ax.plot(row["datetime"][s_ds], row["signal"][s_ds])
    #         eligble = mo[mo[f"{row['label'][:3].lower()}"] == 1].datetime
    #         width = 1.1574074074074075e-05
    #     else:
    #         ax.plot(row["time [s]"][s_ds], row["signal"][s_ds])
    #         eligble = mo[mo[f"{row['label'][:3].lower()}"] == 1]["time [s]"]
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
    #         ax.set_xlim([min(row["time [s]"]), round(max(row["time [s]"]))])

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