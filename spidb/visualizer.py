# %%
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import signal
from dankpy import color
from spidb import spidb, normalization
from dankpy import acoustics
from sqlalchemy import or_

#%%
def waveform_display(
    db:spidb.Database,
    start:datetime.datetime,
    end:datetime.datetime,
    sensor:spidb.Sensor,
    time_format:str="datetime",
    normalize:str="median",
    envelope:bool=False,
    filter:list[float, float]=[500.0, 6000.0],
    external_spl:bool=False,
    size:tuple[float, float]=(6.0, 3.25),
):
    # if compressed:
    fig, axs = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=size)

    channels = [
        channel for channel in sensor.channels if channel.number in [0, 1, 2, 3, 7]
    ]

    for i, c in enumerate(channels):
        a = db.get_audio(start, end, channel_number=c.number, sensor=sensor)

        ax = axs[i]

        if sensor.subname == "A-SPIDS":
            if c.number < 4:
                label = f"Ch. {c.number} - Piezoelectric"
            else:
                if external_spl:
                    spl = normalization.calculate_spl(a.data.signal)
                    spl = normalization.spl_coefficient(spl)
                    label = f"Ch. {c.number} - Microphone (SPL {spl:.2f} dBA)"
                else:
                    label = f"Ch. {c.number} - Microphone"
        else:
            if c.number < 6:
                label = f"Ch. {c.number} - Microwave"
            elif c.number == 6:
                label = f"Ch. {c.number} - Microphone"
            else:
                label = f"Ch. {c.number} - Piezoelectric"

        if filter:
            if sensor.subname == "A-SPIDS":
                if c.number < 4:
                    a.bandpass_filter(filter[0], filter[1], order=10, overwrite=True)
                else:
                    a.bandpass_filter(filter[0], filter[1], order=10, overwrite=True)
                    # a.highpass_filter(500, order=10, overwrite=True)
            else:
                if c.number < 6:
                    a.lowpass_filter(filter[0], order=10, overwrite=True)
                else:
                    a.highpass_filter(filter[0], order=10, overwrite=True)

        if envelope:
            a.envelope(overwrite=True)

        if normalize:
            if sensor.subname == "A-SPIDS":
                if normalize == "median":
                    a = normalization.median_normalize(
                        a, filter="bandpass", low=filter[0], high=filter[1], ratio=4
                    )
                if normalize == "noise":
                    a = normalization.noise_normalize(db, a, channel=c, filter="bandpass", low=filter[0], high=filter[1])

            if sensor.subname == "M-SPIDS":
                if c < 6:
                    a.data.signal = a.data.signal / 0.1 * a.data.signal.max()
                else:
                    level = np.median(a.data.signal)
                    noise = a.data.signal[a.data.signal < level]
                    a.data.signal = a.data.signal / np.sqrt(np.mean(noise**2))

        ax.yaxis.set_label_position("right")

        if time_format == "datetime":
            ax.plot(a.data.datetime, a.data.signal, label=label)
            ax.xaxis.set_ticks(np.arange(a.data.datetime.min(), a.data.datetime.max()))

            myFmt = mdates.DateFormatter("%H:%M:%S")
            ax.xaxis.set_major_formatter(myFmt)
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))

        elif time_format == "seconds":
            ax.plot(a.data["seconds"], a.data.signal, label=label)
            ax.set_xlim(
                [round(a.data["seconds"].min()), round(a.data["seconds"].max())]
            )

        if envelope and normalize and filter:
            ax.set_ylim(0, None)

        ax.legend(loc="center right", handlelength=0, handletextpad=0)

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
    size=(6, 3.5),
    external_spl=False,
):
    if isinstance(sensor, spidb.Sensor) or isinstance(sensor, spidb.models.Sensor):
        sensor = sensor
    else:
        sensor = (
            db.session.query(spidb.Sensor)
            .filter(or_(spidb.Sensor.name == sensor, spidb.Sensor.subname == sensor))
            .first()
        )

    if zmin is None and zmax is None:
        if sensor.subname == "A-SPIDS":
            zmin = -140
            zmax = -80
        else:
            zmin = -100
            zmax = -50

    if section == "internal":
        if sensor.subname == "A-SPIDS":
            fig, axs = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=size)

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
                # add a blank line to the plot to add a label to the legend
                ax.plot(
                    [], [], "", label=f"Ch. {c} (Piezoelectric)"
                )  # this wasn't blank
                ax.legend(
                    loc="center right", handlelength=0, handletextpad=0, fontsize=8,
                )
                # ax.set_ylabel(f"Ch. {c}")
                # ax.yaxis.set_label_position("right")
                # ax.get_yaxis().set_label_coords(1.015, 0.6)
    elif section == "external":
        if sensor.subname == "A-SPIDS":
            fig, axs = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=size)

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
                ax.plot([], [], label=f"Ch. {c}")
                ax.legend(loc="center right")
                axi.set_clim([zmin, zmax])
                # ax.set_ylabel(f"Ch. {c}")
                # ax.yaxis.set_label_position("right")
    elif section == "minimal":
        if sensor.subname == "A-SPIDS":
            fig, axs = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=size)

            channels = np.arange(0, 4).tolist()
            channels.append(7)

            for c, channel in enumerate(channels):
                ax = axs[c]
                a = db.get_audio(start, end, channel_number=channel, sensor=sensor)

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
                # add a blank line to the plot to add a label to the legend
                if channel < 4:
                    ax.plot(
                        [], [], "", label=f"Ch. {channel} (Piezoelectric)"
                    )  # this wasn't blank
                else:
                    if external_spl:
                        spl = normalization.calculate_spl(a.data.signal)
                        spl = normalization.spl_coefficient(spl)
                        ax.plot(
                            [],
                            [],
                            "",
                            label=f"Ch. {channel} (Microphone, {round(spl, 2)} dBA)",
                        )  # this wasn't blank
                    else:
                        ax.plot(
                            [], [], "", label=f"Ch. {channel} (Microphone)"
                        )  # this wasn't blank

                ax.legend(loc="upper right", handlelength=0, handletextpad=0)
    else:
        if sensor.subname == "A-SPIDS":
            fig, axs = plt.subplots(
                nrows=4,
                ncols=2,
                sharex=True,
                sharey=True,
                figsize=size,
                constrained_layout=True,  # <-- ensure this is set
            )
        else:
            fig, axs = plt.subplots(
                nrows=4,
                ncols=2,
                sharex=True,
                figsize=size,
                constrained_layout=True,  # <-- ensure this is set
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

            if sensor.subname == "A-SPIDS":
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

            if sensor.subname == "A-SPIDS":
                if c < 4:
                    ax.plot([], [], "", label=f"Piezoelectric – Ch. {c}")
                else:
                    ax.plot([], [], "", label=f"Microphone – Ch. {c}")
            else:
                if c < 6:
                    ax.plot([], [], "", label=f"Microwave – Ch. {c}")
                elif c == 6:
                    ax.plot([], [], "", label=f"Microphone – Ch. {c}")
                else:
                    ax.plot([], [], "", label=f"Piezoelectric – Ch. {c}")

            ax.yaxis.set_label_position("right")
            ax.legend(loc="center right", handlelength=0, handletextpad=0)
    if time_format == "datetime":
        ax.set_xlim([times.min(), times.max()])
        ax.set_xticks([times.min(), times[len(times) // 2], times.max()])
        myFmt = mdates.DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(myFmt)

    else:
        ax.set_xlim([round(times.min()), round(times.max())])
        # ax.set_xlim([round(times.min()), round(times.max())])  # redundant

    if time_format == "datetime":
        fig.supxlabel(f"Time on {a.data.datetime[0].date()}", fontsize=10)
    else:
        fig.supxlabel("Time [s]", fontsize=10)

    # --- Colorbar placement fix ---
    # Use the last 'axi' for colorbar, and attach to all axes
    if showscale == "top":
        cbar = fig.colorbar(
            axi,
            ax=axs,
            orientation="horizontal",
            location="top",
            aspect=50,
        )
        cbar.ax.set_title("Spectral Power [dB]")
    else:
        cbar = fig.colorbar(
            axi,
            ax=axs,
            orientation="vertical",
            location="right",
            aspect=50,  # uncomment this line
            ticks=[zmin, round(zmin + (zmax - zmin) / 2), zmax],  # uncomment this line
        )
        cbar.ax.set_ylabel("Power [dB]", fontsize=10)
    fig.supylabel("Frequency [Hz]", fontsize=10)

    return fig, axs


def spectra_display(audios, spl=False, colors=None):
    fig, ax = plt.subplots()

    if colors is None:
        colors = color.colors

    for i, a in enumerate(audios):
        a.fade_in(fade_time=1, overwrite=True)
        a.fade_out(fade_time=1, overwrite=True)

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

        p = 10 * np.log10(p)

        if a.channel_number == 7 and spl:
            spl = acoustics.calculate_spl_dba(a.data.signal, a.sample_rate)
            spl = normalization.spl_coefficient(spl)
            ax.plot(f, p, label=f"Ch. {a.channel_number} ({spl:.2f} dBA)", c=colors[i])
        else:
            ax.plot(f, p, label=f"Ch. {a.channel_number}", c=colors[i])

    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Spectral Power [dB]")
    ax.legend(loc="upper right", ncols=len(audios))

    return fig, ax

