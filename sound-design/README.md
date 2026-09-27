# Sound design: `dee-warner-tank_base-edit_v1_720p.mp4`

Music and sound effects for the Dee Warner true-crime edit (42:51).

The base edit leaves digital silence under its graphics and montage inserts.
This adds scored cues there, a very quiet underscore bed under the
interrogation, and sound effects on graphic cards, photos, documents and the
verdict. The original dialogue is untouched: same level before and after.

| Cue | Time | Music |
|---|---|---|
| Cold open | 0:00–0:33 | Dark drone, piano, rising strings into a hit |
| The tracking claims | 9:13–10:14 | Pulsing electronic, data/GPS feel |
| Family / testimony | 14:00–14:41 | Somber piano and cello |
| The night of April 24 | 24:11–24:56 | Eerie drones, heartbeat drum |
| Dale's phone timeline | 37:40–38:39 | Ticking-clock tension |
| Finale: search → verdict | 41:08–42:51 | Driving build, grief, solemn resolution |
| Underscore bed | everywhere else | Low ambient drone at about -42 LUFS, crossfade-looped |

All sound-effect placements and levels are in `cues.json`.

## Sources

- Sound effects: ElevenLabs `text_to_sound_effects`.
- Music: vidIQ `generate_music` (royalty-free). ElevenLabs music generation
  returned 403 because the account hasn't accepted the Eleven Music terms
  (https://elevenlabs.io/music-terms).

The `.wav` music files are actually MP3-encoded; ffmpeg reads them fine.

## Rebuild

Needs `ffmpeg` on PATH. The source video isn't committed (99 MB).

```bash
python3 sound-design/mix.py sound-design/cues.json \
  dee-warner-tank_base-edit_v1_720p.mp4 dee-warner-tank_sfx-music_v1_720p.mp4 \
  --audio-dir sound-design/audio
```

Edit `cues.json` to move, re-level, add or remove cues, then re-run. Video is
stream-copied, so a full re-mix takes under a minute.

---

# ASMR reel: `e672a7a7-reel-silent-h264.MP4`

An 11-second silent pancake reel with close-mic ASMR sounds (ElevenLabs
`text_to_sound_effects`) placed on each cut: peaches, honey drizzle, fork and
knife cuts, yogurt, egg crack, flour, stirring, pan sizzle, spatula flips,
stacking and sugar sprinkle. It has a very quiet room tone underneath and is
mastered to a subtle -20 LUFS. Placements are in `reel-asmr/cues.json`.

Sync is frame-accurate. Each cue gives `hit`, the frame where the action
lands, and `hit_offset`, where the sound's peak sits inside its file, so the
peak lands on that frame (measured within 5 ms). `from` and `until` trim each
sound to its own shot so nothing bleeds across a cut.

```bash
python3 sound-design/mix.py sound-design/reel-asmr/cues.json \
  e672a7a7-reel-silent-h264.MP4 reel_asmr.mp4
```
