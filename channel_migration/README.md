## INSTALLATION

Linux/Ubuntu, etc.

```
apt-get -y update
apt-get install -y ffmpeg
pip install -r requirements.txt
```

Specify the data for the database in the config.ini
Category, channels in preferences.jsonl

## USAGE

Arguments

-l, --link Link to a video, channel, or playlist. Example: -l "https://www.youtube.com/watch?v=VIDEO_EXAMPLE"

-p, --preview Preview video duration. Default: 20 seconds. Example: -p 30

-q, --quality Video quality. Options: "low" mp4,480; "medium" mp4,720; "high" best video + best audio.
Default: best video + best audio. Example: -q "low"

-t, --time Timer-based parsing of a channel/playlist in seconds. Default: 300 seconds (5 minutes). Example: -t 500

-f, --file File with video links for downloading. Example: -f "my/file.txt"

## EXAMPLES

Download video, cover, and preview (30 seconds) with 720p quality using the video link
```
python3 main.py -l "https://www.youtube.com/watch?v=XjNWlzJz2VA" -q 'medium' -p 30 
```

Download videos, covers, and previews (30 seconds) from the channel in the best quality.
Repeat the process every 5 minutes and download new videos if available.
```
python3 main.py -l "https://www.youtube.com/@channel_name" -p 30
```