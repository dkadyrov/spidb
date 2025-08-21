#%%
from sonicdb import audio, utilities
import numpy as np
import pandas as pd
from scipy import signal 
from copy import deepcopy
from spidb import spidb
from sqlalchemy.orm import object_session
noise_data = [
    dict(
        start=utilities.read_datetime("2023-05-31 17:32:00"),
        end=utilities.read_datetime("2023-05-31 17:33:00"),
    ),
    dict(
        start=utilities.read_datetime("2023-09-26 16:02:00"),
        end=utilities.read_datetime("2023-09-26 16:02:30"),
    ),
    dict(
        start=utilities.read_datetime("2023-10-23 12:55:00"),
        end=utilities.read_datetime("2023-10-23 12:55:10"),
    ),
]

correction_coefficients = [1.014732897991385, 1.0180935308718362, 1.0111353229903404, 1.0101224163268911]

# def spl_coefficient(spl, m=0.9295575436489893, b=32.81146264832007): 
    # return m * spl + b

def spl_coefficient(spl, m=1.5078675371343309, b=-1.3239939533445408): 
    return m * spl + b


def reference_signal(db, sensor, channels=[0, 1, 2, 3]):
    sensor = db.get_sensor(sensor)

    reference = pd.DataFrame()

    for n in noise_data:
        for channel in channels:
            a = db.get_audio(
                start=n["start"],
                end=n["end"],
                sensor=sensor,
                channel_number=channel,
            )

            a.fade_in(fade_time=5, overwrite=True)
            a.fade_out(fade_time=5, overwrite=True)

            f, p = signal.welch(
                a.data.signal,
                fs=a.sample_rate,
                nperseg=1024,
                window="blackmanharris",
                scaling="spectrum",
                average="mean",
            )

            if channel == 0:
                reference["frequency"] = f

            reference[f"Ch. {channel}"] = 10 * np.log10(p)
    
    # Average the across the channels
    reference["average"] = reference.iloc[:, 1:].mean(axis=1)

    return reference


def noise_coefficient(db, sensor, channel, filter="bandpass", low=500, high=6000, order=10): 
    sensor = db.get_sensor(sensor)
    channel = db.get_channel(channel)

    coefficient = 0 

    for n in noise_data:
        a = db.get_audio(
            start=n["start"],
            end=n["end"],
            sensor=sensor,
            channel_number=channel.number,
        )

        a.fade_in(fade_time=2, overwrite=True)
        a.fade_out(fade_time=2, overwrite=True)

        if filter == "bandpass":
            a.bandpass_filter(low, high, order=order, overwrite=True)
        elif filter == "lowpass":
            a.lowpass_filter(high, order=order, overwrite=True)
        elif filter == "highpass":
            a.highpass_filter(low, order=order, overwrite=True)

        a.envelope(overwrite=True)

        rms = np.sqrt(np.mean(a.data.signal**2))

        coefficient += rms

    return coefficient / len(noise_data)



def noise_spl(db, sensor, channel):
    sensor = db.get_sensor(sensor)
    channel = db.get_channel(channel)

    spl = pd.DataFrame()

    p = None
    for n in noise_data:
        a = db.get_audio(
            start=n["start"],
            end=n["end"],
            sensor=sensor,
            channel_number=channel.number,
        )

        a.fade_in(fade_time=2, overwrite=True)
        a.fade_out(fade_time=2, overwrite=True)

        f, p = signal.welch(
            a.data.signal,
            fs=a.sample_rate,
            nperseg=1024,
            window="blackmanharris",
            scaling="spectrum",
            average="mean",
        )

        if p is None:
            p += 10 * np.log10(p)
        else: 
            p = 10 * np.log10(p)

    spl["frequency"] = f
    spl["power"] = p

    return spl

def noise_normalize(a:audio.Audio, channel:spidb.models.Channel, filter="bandpass", low=500, high=6000) -> audio.Audio:
    """
    Normalize the audio signal by the noise level.

    Args:
        a (sonicdb.Audio): the audio signal
        channel (int): the channel number

    Returns:
        sonicdb.Audio: the normalized audio signal
    """
    if channel.gain == 0 or channel.gain is None: 
        coefficient = noise_coefficient(channel.sensor, channel, filter, low, high, order)
    else:
        coefficient = channel.gain

    a.data.signal = a.data.signal / coefficient
    a.audio = a.audio / coefficient

    return a 


def median_normalize(signal, filter=None, low=None, high=None, ratio=0.5):
    a = deepcopy(signal)

    if filter == "bandpass":
        a.bandpass_filter(low, high, order=10, overwrite=True)
    elif filter == "lowpass":
        a.lowpass_filter(high, order=10, overwrite=True)
    elif filter == "highpass":
        a.highpass_filter(low, order=10, overwrite=True)

    level = ratio * np.median(a.data.signal)

    noise = a.data[a.data.signal <= level]
    rms = np.sqrt(np.mean(noise.signal**2))

    a.data.signal = a.data.signal / rms
    a.audio = a.audio / rms

    return a


def calculate_nsel(audio, filter="bandpass", low=None, high=None, channel=None, db=None):
    a = deepcopy(audio)

    n_spl = noise_spl(db, channel.sensor, channel)

    a.fade_in(1, overwrite=True)
    a.fade_out(1, overwrite=True)

    f, p = signal.welch(
        a.data.signal,
        fs=a.sample_rate,
        nperseg=1024,
        window="blackmanharris",
        scaling="spectrum",
        average="mean",
    )

    p = 10 * np.log10(p)
    n = n_spl["power"]

    if filter == "bandpass":
        p = p[(f >= low) & (f <= high)]
        n = n[(f >= low) & (f <= high)]
    elif filter == "lowpass":
        p = p[f <= high]
        n = n[f <= high]
    elif filter == "highpass":
        p = p[f >= low]
        n = n[f >= low]

    spl = 10 * np.log10(np.sum(10 ** (p / 10)))
    npl = 10 * np.log10(np.sum(10 ** (n / 10)))

    snr = spl - npl

    return snr

def calculate_nspa(audio, filter="bandpass", low=None, high=None, normalize="noise", channel=None, ratio=None):
    a = deepcopy(audio)

    if normalize == "noise":
        a = noise_normalize(a, channel)
    elif normalize == "median":
        a = median_normalize(a, channel, ratio)

    a.fade_in(1, overwrite=True)
    a.fade_out(1, overwrite=True)

    if filter == "bandpass":
        a.bandpass_filter(low, high, order=10, overwrite=True)
    elif filter == "lowpass":
        a.lowpass_filter(high, order=10, overwrite=True)
    elif filter == "highpass":
        a.highpass_filter(low, order=10, overwrite=True)
    
    a.envelope(overwrite=True)

    min_threshold = 0.5 * np.max(a.data.signal)
    max_threshold = 0.9 * np.max(a.data.signal)
    cutoff = a.data.signal[a.data.signal >= min_threshold]
    cutoff = cutoff[cutoff <= max_threshold]

    rms = np.sqrt(np.mean(cutoff**2))
    amp = 20 * np.log10(rms)

    return amp

def nspa(signal):
    min_threshold = 0.5 * np.max(signal)
    max_threshold = 0.9 * np.max(signal)
    cutoff = signal[signal >= min_threshold]
    cutoff = cutoff[cutoff <= max_threshold]

    rms = np.sqrt(np.mean(cutoff**2))
    amp = 20 * np.log10(rms)

    return amp    
