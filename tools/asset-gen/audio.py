"""Chiptune sound effects and a seamless music loop, synthesised with numpy.

Every sound is written as .ogg (Vorbis) and .mp3 so Phaser can pick whichever
the browser supports: this.load.audio(key, [ogg, mp3]).
"""
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

from common import OUT

SR = 44100


def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def note(n):
    """MIDI note number -> Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def square(freq, dur, duty=0.5):
    t = t_axis(dur)
    phase = np.cumsum(np.broadcast_to(freq, t.shape) / SR) % 1.0
    return np.where(phase < duty, 1.0, -1.0)


def triangle(freq, dur):
    t = t_axis(dur)
    phase = np.cumsum(np.broadcast_to(freq, t.shape) / SR) % 1.0
    return 4 * np.abs(phase - 0.5) - 1


def sine(freq, dur):
    t = t_axis(dur)
    phase = np.cumsum(np.broadcast_to(freq, t.shape) / SR)
    return np.sin(2 * np.pi * phase)


def noise(dur, seed=0):
    rng = np.random.default_rng(seed)
    return rng.uniform(-1, 1, int(SR * dur))


def env(n, attack=0.005, release=0.08, sustain=1.0, curve=2.0):
    total = n / SR
    t = np.arange(n) / SR
    e = np.ones(n) * sustain
    a = t < attack
    e[a] = t[a] / attack
    r = t > total - release
    e[r] = sustain * ((total - t[r]) / release) ** curve
    return np.clip(e, 0, 1)


def decay(n, rate):
    return np.exp(-np.arange(n) / SR * rate)


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[: len(p)] += p
    return out


def seq(*parts, gap=0.0):
    pad = np.zeros(int(SR * gap))
    out = []
    for p in parts:
        out += [p, pad]
    return np.concatenate(out)


def lowpass(x, alpha=0.25):
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc)
        y[i] = acc
    return y


def blip(n_or_hz, dur, duty=0.25, vol=0.5, rate=18):
    s = square(n_or_hz, dur, duty)
    return s * env(len(s), 0.002, dur * 0.4) * decay(len(s), rate) * vol


# --- Sound effects -------------------------------------------------------------
def sfx_pickup():
    return seq(blip(note(88), 0.055, 0.25, 0.45, 10), blip(note(95), 0.11, 0.25, 0.45, 14))


def sfx_pickup_rare():
    notes = [84, 88, 91, 96, 100]
    parts = [mix(blip(note(n), 0.07, 0.125, 0.4, 8), triangle(note(n - 12), 0.07) * 0.2 * env(int(SR * 0.07)))
             for n in notes]
    tail = mix(triangle(note(103), 0.35) * 0.35 * decay(int(SR * 0.35), 7),
               square(note(108), 0.35, 0.125) * 0.12 * decay(int(SR * 0.35), 9))
    return seq(*parts, tail)


def sfx_beaten():
    dur = 0.32
    f = np.linspace(note(64), note(46), int(SR * dur))
    s = square(f, dur, 0.5) * 0.35 + square(f * 1.01, dur, 0.5) * 0.2
    return s * env(len(s), 0.003, 0.1) * decay(len(s), 4)


def sfx_spawn():
    dur = 0.3
    f = np.linspace(note(72), note(96), int(SR * dur))
    s = sine(f, dur) * 0.35 * env(int(SR * dur), 0.02, 0.15)
    sparkle = mix(blip(note(100), 0.05, 0.125, 0.15), np.zeros(int(SR * 0.12)))
    return mix(s, np.concatenate([np.zeros(int(SR * 0.18)), sparkle]))


def sfx_countdown_tick():
    return blip(note(81), 0.12, 0.5, 0.45, 12)


def sfx_countdown_go():
    dur = 0.5
    s = mix(square(note(88), dur, 0.25) * 0.3, square(note(93), dur, 0.25) * 0.25, triangle(note(76), dur) * 0.3)
    return s * env(len(s), 0.004, 0.25)


def sfx_match_end():
    melody = [(84, 0.12), (88, 0.12), (91, 0.12), (96, 0.45)]
    parts = []
    for n, d in melody:
        s = mix(square(note(n), d, 0.25) * 0.3, triangle(note(n - 12), d) * 0.3)
        parts.append(s * env(len(s), 0.004, d * 0.5))
    return seq(*parts, gap=0.02)


def sfx_ui_click():
    return blip(note(96), 0.035, 0.5, 0.3, 40)


def sfx_ui_hover():
    return blip(note(100), 0.025, 0.125, 0.12, 60)


def sfx_tx_confirm():
    return seq(blip(note(103), 0.03, 0.125, 0.18, 30), blip(note(108), 0.04, 0.125, 0.15, 30))


def sfx_join():
    return seq(blip(note(79), 0.06, 0.25, 0.35, 12), blip(note(86), 0.09, 0.25, 0.35, 12))


# --- Music loop ------------------------------------------------------------------
def music_loop():
    bpm = 128
    beat = 60 / bpm
    step = beat / 4  # 16th notes
    bars = 8
    total = int(SR * step * 16 * bars)
    out = np.zeros(total)
    # A minor: Am - F - C - G, twice
    chords = [(57, [69, 72, 76]), (53, [65, 69, 72]), (48, [64, 67, 72]), (55, [67, 71, 74])] * 2
    arp_pattern = [0, 1, 2, 1, 0, 2, 1, 2, 0, 1, 2, 1, 2, 1, 0, 1]
    lead = [76, None, 74, 72, None, 72, 74, None, 76, None, 79, None, 76, 74, 72, None]
    for b, (bass, triad) in enumerate(chords):
        bar0 = int(SR * step * 16 * b)
        for s in range(16):
            i0 = bar0 + int(SR * step * s)
            # arpeggio
            n = triad[arp_pattern[s]] + (12 if b % 4 == 3 and s >= 12 else 0)
            a = square(note(n), step * 0.9, 0.125) * 0.07
            a *= env(len(a), 0.002, step * 0.5)
            out[i0:i0 + len(a)] += a[: total - i0]
            # bass on 8ths
            if s % 2 == 0:
                bn = bass - 12 + (7 if s in (6, 14) else 0)
                bl = triangle(note(bn), step * 1.8) * 0.22
                bl *= env(len(bl), 0.003, step * 0.6)
                out[i0:i0 + len(bl)] += bl[: total - i0]
            # kick on beats
            if s % 4 == 0:
                kd = 0.16
                f = np.linspace(150, 45, int(SR * kd))
                k = sine(f, kd) * 0.45 * decay(int(SR * kd), 22)
                out[i0:i0 + len(k)] += k[: total - i0]
            # snare on 2 and 4
            if s in (4, 12):
                sn = lowpass(noise(0.12, b * 16 + s), 0.6) * 0.22 * decay(int(SR * 0.12), 28)
                out[i0:i0 + len(sn)] += sn[: total - i0]
            # hats on off-8ths
            if s % 2 == 1:
                h = noise(0.03, s) * 0.06 * decay(int(SR * 0.03), 90)
                h = h - lowpass(h, 0.3)
                out[i0:i0 + len(h)] += h[: total - i0]
            # lead melody on bars 5-8
            if b >= 4 and lead[s] is not None:
                ln = lead[s] + (0 if b % 2 == 0 else -2 if s > 8 else 0)
                vib = 1 + 0.004 * np.sin(2 * np.pi * 6 * t_axis(step * 1.7))
                l = square(note(ln) * vib, step * 1.7, 0.25) * 0.08
                l *= env(len(l), 0.004, step * 0.8)
                out[i0:i0 + len(l)] += l[: total - i0]
    return out


# --- Export --------------------------------------------------------------------
def write(name, data, folder="audio/sfx"):
    data = np.asarray(data, dtype=np.float64)
    peak = np.max(np.abs(data)) or 1.0
    data = data / peak * 0.85
    pcm = (data * 32767).astype(np.int16)
    dest = OUT / folder
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / f"{name}.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        for ext, args in (("ogg", ["-c:a", "libvorbis", "-q:a", "4"]), ("mp3", ["-c:a", "libmp3lame", "-b:a", "96k"])):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), *args, str(dest / f"{name}.{ext}")],
                           check=True)


SFX = {
    "pickup": sfx_pickup,
    "pickup-rare": sfx_pickup_rare,
    "beaten": sfx_beaten,
    "spawn": sfx_spawn,
    "countdown-tick": sfx_countdown_tick,
    "countdown-go": sfx_countdown_go,
    "match-end": sfx_match_end,
    "ui-click": sfx_ui_click,
    "ui-hover": sfx_ui_hover,
    "tx-confirm": sfx_tx_confirm,
    "join": sfx_join,
}


def build():
    for name, fn in SFX.items():
        write(name, fn())
    write("arena-loop", music_loop(), "audio/music")
    return list(SFX)


if __name__ == "__main__":
    build()
