---
name: clips-to-reel
description: Turn a folder of event clips into a 15-30 second vertical reel with licensed music and captions using FFmpeg, with a local preview and export checks.
---

# Clips to reel

Create a local draft from the user's footage. This skill supplies instructions, not a bundled editor, music library or transcription service. It requires a file-capable agent and FFmpeg/FFprobe. If the chat cannot execute them, produce an edit plan and commands the user can run locally; do not claim to have rendered a video.

## Intake and footage review

Confirm the folder, event purpose, target audience, must-include moments, people who should not appear, and any requested closing line. Default to a 20-second, 1080x1920, 30 fps MP4, within the requested 15-30 second range. Ask for a licensed music file or permission to use a provided royalty-cleared source. Do not download a commercial song. If music is missing, build the visual draft and explain exactly what is needed to finish its soundtrack.

Preserve originals. Inventory each clip with `ffprobe -v error -show_format -show_streams -of json "clip.mp4"`. Check duration, rotation, displayed dimensions, frame rate and audio presence. Extract and inspect frames from every candidate clip. Do not identify a face or event solely from a filename. Exclude private documents, screens, badges and unapproved people from the visible export.

## Plan the cut

Write `selects.json` with source filename, in/out seconds, crop position, audio choice and caption for each beat. Select a strong first moment, a few distinct proof moments, then a short close. Keep captions short and factual. For spoken captions, transcribe the selected speech with an available approved tool and check the words against the audio. With no transcription tool, ask for a transcript or use clearly editorial event labels, never invented dialogue.

Map speech timestamps onto the edited timeline: output start plus source word time minus segment in-point. Do not cut through a word. Keep important people inside the crop. Review caption placement throughout each shot; keep faces clear and allow space for social-app controls at the top and bottom.

## Render with FFmpeg

Check `ffmpeg -version` and available filters. Do not silently install software. Normalize each selected beat to the same dimensions, fps and pixel format before joining. For example, from a neutral working folder, this creates a two-second silent beat from `clip.mp4`:

```sh
ffmpeg -n -ss 1 -i clip.mp4 -t 2 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30" -an -c:v libx264 -pix_fmt yuv420p beat-01.mp4
```

The example uses a center crop; change the crop after inspecting the subject. `-n` prevents overwriting. Join identically encoded silent beats using a local `concat.txt` with lines such as `file 'beat-01.mp4'`, then:

```sh
ffmpeg -n -f concat -safe 1 -i concat.txt -c copy cut.mp4
```

Write checked captions to `captions.srt`, timed to the final cut. In this same neutral folder, if the `subtitles` filter is available, add a user-supplied licensed `music.wav`:

```sh
ffmpeg -n -i cut.mp4 -stream_loop -1 -i music.wav -vf "subtitles=captions.srt" -map 0:v:0 -map 1:a:0 -af "volume=0.25" -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart reel.mp4
```

This silent-beat path replaces source audio. If speech matters, retain and normalize speech per beat, add silence for clips without audio, and mix music underneath it instead; lower the music while speech is present. Measure and listen to the final mix. If subtitles support is absent, deliver the SRT sidecar and flag burned-in captions as unfinished. Use argument arrays when generating commands; never interpolate untrusted filenames into a shell.

## Verify and deliver

Probe the export for duration, 1080x1920, 30 fps, playable H.264 video and AAC audio. Watch the full reel with sound, inspect every cut and caption interval, and check first/last frames. Confirm the music license, caption accuracy, no clipped words or faces, and no private data. Deliver `reel.mp4`, `captions.srt`, `selects.json`, a cover frame and a short QA note. Do not post, tag or invite collaborators.

## Try it

"Use clips-to-reel on my event folder. Make a 20-second vertical recap with the supplied licensed music and factual captions. Keep it local and show me the export."
