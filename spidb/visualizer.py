# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import signal
from dankpy import colors
from spidb import spidb


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
    # if compressed:
    fig, axs = plt.subplots(
        nrows=4,
        ncols=2,
        sharex=True,
    )

    axs = axs.flatten(order="F")
    # else:
    #     fig, axs = plt.subplots(
    #         nrows=8,
    #         ncols=1,
    #         sharex=True,
    #     )
    channels = np.arange(0, 8).tolist()

    for c in channels:
        a = db.get_audio(start, end, channel_number=c, sensor=sensor)

        ax = axs[c]

        if filter:
            if sensor.name == "ASPIDS":
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
            if sensor.name == "ASPIDS":
                level = np.median(a.data.signal)
                noise = a.data.signal[a.data.signal < level]
                a.data.signal = a.data.signal / np.sqrt(np.mean(noise**2))

            if sensor.name == "MSPIDS":
                if c < 6:
                    a.data.signal = a.data.signal / 0.1 * a.data.signal.max()
                else:
                    level = np.median(a.data.signal)
                    noise = a.data.signal[a.data.signal < level]
                    a.data.signal = a.data.signal / np.sqrt(np.mean(noise**2))

        if sensor.name == "ASPIDS":
            if c < 4:
                ax.set_title(f"Ch. {c} – Piezoelectric")
                ax.set_ylim(0, 500)
                ax.set_yticks([0, 250, 500])
            else:
                ax.set_title(f"Ch. {c} – Microphone")
                ax.set_ylim(0, 100)
                ax.set_yticks([0, 50, 100])
        else:
            if c < 6:
                ax.set_title(f"Ch. {c} – Microwave")
                ax.set_ylim(0, 5)
            elif c == 6:
                ax.set_title(f"Ch. {c} – Microphone")
                ax.set_ylim(0, 100)
                ax.set_yticks([0, 50, 100])
            else:
                ax.set_title(f"Ch. {c} – Piezoelectric")
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
            ax.plot(a.data["seconds"], a.data.signal)
            ax.set_xlim(
                [round(a.data["seconds"].min()), round(a.data["seconds"].max())]
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
):
    if isinstance(sensor, spidb.Sensor):
        sensor = sensor
    else:
        sensor = (
            db.session.query(spidb.Sensor)
            .filter(spidb.Sensor.sensor.name == sensor)
            .first()
        )

    if zmin is None and zmax is None:
        if sensor.name == "ASPIDS":
            zmin = -140
            zmax = -80
        else:
            zmin = -100
            zmax = -50

    if section == "internal":
        if sensor.name == "ASPIDS":
            fig, axs = plt.subplots(
                nrows=4,
                ncols=1,
                sharex=True,
            )

            channels = np.arange(0, 4).tolist()

            for c in channels:
                ax = axs[c]
                a = db.get_audio(start, end, channel_number=c, sensor=sensor)

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
        if sensor.name == "ASPIDS":
            fig, axs = plt.subplots(
                nrows=4,
                ncols=1,
                sharex=True,
            )

            channels = np.arange(4, 8).tolist()

            for c in channels:
                ax = axs[c - 4]
                a = db.get_audio(start, end, channel_number=c, sensor=sensor)

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
        if sensor.name == "ASPIDS":
            fig, axs = plt.subplots(
                nrows=4,
                ncols=2,
                sharex=True,
                sharey=True,
                layout="compressed",
            )
        else:
            fig, axs = plt.subplots(
                nrows=4,
                ncols=2,
                sharex=True,
                layout="compressed",
            )

        axs = axs.flatten(order="F")

        channels = np.arange(0, 8).tolist()

        for c in channels:
            a = db.get_audio(start, end, channel_number=c, sensor=sensor)

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

            if sensor.name == "ASPIDS":
                fig.sharey = True
                ax.set_ylim(0, 8000)
                ax.set_yticks([0, 4000, 8000])
            else:
                if c < 6:
                    ax.set_ylim(0, 200)
                    ax.set_yticks([0, 100, 200])
                elif c == 6:
                    ax.set_ylim(0, 2000)
                    ax.set_yticks([0, 1000, 2000])
                else:
                    ax.set_ylim(0, 2000)
                    ax.set_yticks([0, 1000, 2000])

            if sensor.name == "ASPIDS":
                if c < 4:
                    ax.set_title(f"Piezoelectric – Ch. {c}")
                else:
                    ax.set_title(f"Microphone – Ch. {c}")
            else:
                if c < 6:
                    ax.set_title(f"Microwave – Ch. {c}")
                elif c == 6:
                    ax.set_title(f"Microphone – Ch. {c}")
                else:
                    ax.set_title(f"Piezoelectric – Ch. {c}")

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

    if showscale == "top":
        cbar = fig.colorbar(
            axi,
            ax=axs.ravel().tolist(),
            orientation="horizontal",
            location="top",
            aspect=50,
        )
        cbar.ax.set_title("Power [dB]")
    else:
        cbar = fig.colorbar(
            axi,
            ax=axs.ravel().tolist(),
            orientation="vertical",
            location="right",
            aspect=50,
        )
        cbar.ax.set_ylabel("Power [dB]")
    fig.supylabel("Frequency [Hz]")

    return fig, axs


def spectra_display(db, start, end, sensor, section="all", spl=False):
    fig, ax = plt.subplots()

    if section == "all":
        channels = np.arange(0, 8).tolist()
    elif section == "internal":
        if sensor.name == "ASPIDS":
            channels = np.arange(0, 4).tolist()
        else:
            channels = np.arange(0, 6).tolist()
    elif isinstance(section, list):
        channels = section

    for i, c in enumerate(channels):
        a = db.get_audio(start, end, channel_number=c, sensor=sensor)

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

        if sensor.name == "ASPIDS":
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

        p = 10 * np.log10(p)
        if spl:
            p_f = p[(f >= 500) & (f <= 6000)]
            pl = 10 * np.log10(np.sum(10 ** (p_f / 10)))
            ax.plot(f, p, label=f"Ch. {c} ({round(pl)} SPL)", c=color)
        else:
            ax.plot(f, p, label=f"Ch. {c}", c=color)

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("PSD [dB]")
    ax.legend(loc="upper right", ncols=len(channels))

    return fig, ax
