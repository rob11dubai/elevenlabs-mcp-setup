#!/usr/bin/env python3
"""Mix music cues, an underscore bed and sound effects into a video.

Usage:
    python3 mix.py cues.json input.mp4 output.mp4 [--audio-dir DIR]

The cue sheet (see cues.json) lists:
  - "music": cues placed at a start time, trimmed to a length, faded in/out and
    loudness-matched to a target LUFS.
  - "bed": one track looped (with crossfades) under the whole video at a low
    level, faded out wherever a music cue plays.
  - "sfx": one-shots placed at a time, peak-normalised to a target dBFS.

The original audio is kept at its original level; a silent video gets a
silent base track. Needs ffmpeg on PATH.
"""
import argparse
import json
import os
import re
import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def duration(path):
    out = run(["ffmpeg", "-hide_banner", "-i", path]).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def has_audio(path):
    return "Audio:" in run(["ffmpeg", "-hide_banner", "-i", path]).stderr


def loudness(path):
    out = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"]).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


def peak(path):
    out = run(["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"]).stderr
    return float(re.search(r"max_volume: (-?[\d.]+) dB", out).group(1))


def build_bed(bed, total, audio_dir, workdir):
    """Loop the bed track with crossfades until it covers the whole video."""
    src = os.path.join(audio_dir, bed["file"])
    xf = bed.get("crossfade", 6)
    length = duration(src)
    copies = max(1, int((total - xf) // (length - xf)) + 1)
    out = os.path.join(workdir, "bed_looped.wav")
    inputs, chain, last = [], [], "[0:a]"
    for i in range(copies):
        inputs += ["-i", src]
    for i in range(1, copies):
        label = f"[x{i}]"
        chain.append(f"{last}[{i}:a]acrossfade=d={xf}:c1=tri:c2=tri{label}")
        last = label
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inputs]
    if chain:
        cmd += ["-filter_complex", ";".join(chain), "-map", last]
    cmd += ["-t", f"{total:.3f}", "-ar", "48000", "-ac", "2", out]
    r = run(cmd)
    if r.returncode:
        sys.exit(r.stderr)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cues")
    ap.add_argument("video")
    ap.add_argument("output")
    ap.add_argument("--audio-dir", default=None)
    args = ap.parse_args()

    sheet = json.load(open(args.cues))
    audio_dir = args.audio_dir or os.path.dirname(os.path.abspath(args.cues))
    workdir = os.path.dirname(os.path.abspath(args.output))
    total = duration(args.video)

    inputs = ["-i", args.video]
    if has_audio(args.video):
        filters = ["[0:a]aresample=48000,aformat=channel_layouts=stereo[orig]"]
    else:
        filters = [f"anullsrc=r=48000:cl=stereo,atrim=0:{total:.3f}[orig]"]
    labels = ["[orig]"]
    n = 1

    # Music cues: trim, fade, loudness-match, place.
    windows = []
    for i, c in enumerate(sheet.get("music", [])):
        path = os.path.join(audio_dir, c["file"])
        length = min(c.get("length", 1e9), duration(path))
        gain = c.get("lufs", sheet.get("music_lufs", -22)) - loudness(path)
        fi, fo = c.get("fade_in", 0.05), c.get("fade_out", 2.0)
        start = c["start"]
        windows.append((start, start + length))
        inputs += ["-i", path]
        filters.append(
            f"[{n}:a]atrim=0:{length:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
            f"afade=t=in:st=0:d={fi},afade=t=out:st={max(0, length - fo):.3f}:d={fo},"
            f"volume={gain:.2f}dB,adelay={int(start * 1000)}:all=1[m{i}]"
        )
        labels.append(f"[m{i}]")
        n += 1

    # Underscore bed: looped, quiet, faded out around every music cue.
    bed = sheet.get("bed")
    if bed:
        path = build_bed(bed, total, audio_dir, workdir)
        gain = bed.get("lufs", -42) - loudness(path)
        ramp = bed.get("duck_ramp", 2.0)
        env = "*".join(
            f"clip(max(({s - 0.5:.2f}-t)/{ramp},(t-{e:.2f})/{ramp}),0,1)" for s, e in windows
        ) or "1"
        inputs += ["-i", path]
        filters.append(f"[{n}:a]volume={gain:.2f}dB,volume='{env}':eval=frame[bed]")
        labels.append("[bed]")
        n += 1

    # Sound effects: peak-normalise each file, then place every hit.
    peaks = {}
    for i, s in enumerate(sheet.get("sfx", [])):
        path = os.path.join(audio_dir, s["file"])
        if path not in peaks:
            peaks[path] = peak(path)
        gain = s.get("peak", -12) - peaks[path]
        # "hit" = when the sound's loudest moment should land; shift the file so it does.
        at = s["at"] if "at" in s else s["hit"] - s["hit_offset"]
        # "until" = trim at a shot cut so nothing bleeds into the next shot.
        # "from" = the shot's own cut; drop any lead-in that would start before it.
        head = max(0.0, s.get("from", at) - at)
        at += head
        trim = ""
        if "until" in s or head:
            length = s.get("until", 1e6) - at
            trim = f"atrim={head:.3f}:{head + length:.3f},asetpts=PTS-STARTPTS,"
            if head:
                trim += "afade=t=in:d=0.01,"
            if "until" in s:
                trim += f"afade=t=out:st={max(0, length - 0.06):.3f}:d=0.06,"
        inputs += ["-i", path]
        filters.append(
            f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,{trim}volume={gain:.2f}dB,"
            f"adelay={int(round(at * 1000))}:all=1[s{i}]"
        )
        labels.append(f"[s{i}]")
        n += 1

    graph = ";".join(filters) +";" + "".join(labels) + (
        f"amix=inputs={len(labels)}:duration=first:normalize=0,"
        "alimiter=limit=0.89:level=false"
        + (f",loudnorm=I={sheet['master_lufs']}:TP=-1.5:LRA=11,aresample=48000" if "master_lufs" in sheet else "")
        + "[out]"
    )
    script = os.path.join(workdir, "filtergraph.txt")
    open(script, "w").write(graph)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y", *inputs,
        "-filter_complex_script", script,
        "-map", "0:v", "-map", "[out]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        args.output,
    ]
    print(f"Mixing {len(labels) - 1} layers into {args.output} ...")
    r = subprocess.run(cmd)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
