# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import signal
from dankpy import colors

# %%
def waveform_display(db, start, end, sensor, normalize=False, time_format="datetime"):
    fig, axs = plt.subplots(
        nrows=8, ncols=1, sharex=True, layout="compressed", figsize=(1.5 * 6, 1.5 * 6)
    )
    # fig, axs = plt.subplots(nrows=8, ncols=1, sharex=True, layout="compressed")
    channels = np.arange(0, 8).tolist()

    for c in channels:
        a = db.get_audio(start, end, channel=c, sensor=sensor)

        if normalize:
            level = 2 * np.median(a.data.signal)
            noise = a.data.signal[a.data.signal < level]
            a.data.signal = a.data.signal / np.sqrt(np.mean(noise**2))

        if sensor == "Acoustic":
            if c < 4:
                ax = axs[c * 2]
                ax.set_ylabel(f"Ch{c} Piezo", rotation=0, horizontalalignment="left")
            else:
                ax = axs[c - (7 - c)]
                ax.set_ylabel(
                    f"Ch{c} Microphone", rotation=0, horizontalalignment="left"
                )
            ax.set_ylim([0, 6000])
            ax.set_yticks([0, 6000])

        else:
            ax = axs[c]
            if c < 6:
                ax.set_ylabel(
                    f"Ch{c} Microwave", rotation=0, horizontalalignment="left"
                )
                ax.set_ylim([-0.2, 0.2])

            else:
                if c == 6:
                    ax.set_ylabel(
                        f"Ch{c} Microphone", rotation=0, horizontalalignment="left"
                    )
                    ax.set_ylim([-1, 1])
                else:
                    ax.set_ylabel(
                        f"Ch{c} Piezo", rotation=0, horizontalalignment="left"
                    )
                    ax.set_ylim([-1, 1])
        ax.yaxis.set_label_position("right")

        ax.get_yaxis().set_label_coords(1.01, 0.6)

        if time_format == "datetime":
            ax.plot(a.data.datetime, a.data.signal)
            ax.xaxis.set_ticks(np.arange(a.data.datetime.min(), a.data.datetime.max()))

            myFmt = mdates.DateFormatter("%H:%M:%S")
            ax.xaxis.set_major_formatter(myFmt)
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))

        else:
            ax.plot(a.data["time [s]"], a.data.signal)
            ax.set_xlim(
                [round(a.data["time [s]"].min()), round(a.data["time [s]"].max())]
            )

    if time_format == "datetime":
        fig.supxlabel(f"Time on {a.data.datetime.iloc[0].date()}")
    else:
        fig.supxlabel("Time [s]")
    fig.supylabel("Amplitude [a.u.]")

    return fig, axs

def spectrogram_display(
    db,
    start,
    end,
    sensor,
    time_format="datetime",
    section="all",
    showscale=False,
    zmin=-140,
    zmax=-80
):
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
                        method="datetime",
                    )
                elif time_format == "seconds":
                    times, frequencies, spectrogram = a.spectrogram(
                        window="hann",
                        window_size=1024,
                        nperseg=1024,
                        nfft=1024,
                        noverlap=512,
                        method="seconds",
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
                        method="datetime",
                    )
                elif time_format == "seconds":
                    times, frequencies, spectrogram = a.spectrogram(
                        window="hann",
                        window_size=1024,
                        nperseg=1024,
                        nfft=1024,
                        noverlap=512,
                        method="seconds",
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
        fig, axs = plt.subplots(
            nrows=8, ncols=1, sharex=True, layout="compressed", figsize=(5.5, 5.5)
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
                    method="datetime",
                )

            elif time_format == "seconds":
                times, frequencies, spectrogram = a.spectrogram(
                    window="hann",
                    window_size=1024,
                    nperseg=1024,
                    nfft=1024,
                    noverlap=512,
                    method="seconds",
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
            ax.set_ylabel(f"Ch. {c}")
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
        # cbar = fig.colorbar(
        #     axi, ax=axs.ravel().tolist(), orientation="horizontal", location="top"
        # )
        cbar = fig.colorbar(
            axi, ax=axs.ravel().tolist(), orientation="vertical", location="right"
        )
        cbar.ax.set_ylabel("Power [dB]")
    fig.supylabel("Frequency [Hz]")

    return fig, axs

def spectra_display(db, start, end, sensor, section="all"):

    fig, ax = plt.subplots()

    if section == "internal":
        if sensor == "Acoustic":
            channels = np.arange(0, 4).tolist()

            for c in channels:
                a = db.get_audio(start, end, channel=c, sensor=sensor)


                a.fade_in(fade_time=2, overwrite=True)
                a.fade_out(fade_time=2, overwrite=True)

                f, p = signal.welch(
                    a.data.signal,
                    fs=a.sample_rate,
                    nperseg=1024,
                    window="blackmanharris",
                    average="mean",
                    scaling="spectrum",
                )

                ax.plot(f, 10 * np.log10(p), label=f"Ch. {c}", color=colors[c])

    if section == "all":
        if sensor == "Acoustic":
            channels = np.arange(0, 8).tolist()

            for c in channels:
                a = db.get_audio(start, end, channel=c, sensor=sensor)

                a.fade_in(fade_time=2, overwrite=True)
                a.fade_out(fade_time=2, overwrite=True)

                f, p = signal.welch(
                    a.data.signal,
                    fs=a.sample_rate,
                    window="blackmanharris",
                    average="mean",
                    scaling="spectrum",
                )

                if c < 4:
                    color = "black"
                else:
                    color = "red"


                ax.plot(f, 10 * np.log10(p), label=f"Ch. {c}", c = color)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("PSD [dB]")
    ax.legend(loc="upper right", ncols=2)