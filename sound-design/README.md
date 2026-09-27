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
