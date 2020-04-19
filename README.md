# spdl.py
Download full south park seasons and episodes. Provides a **command line interface** and can also be imported as a **python southpark library**. This single-file script is designed to be as small, as fast, as easy to use and as independent as possible.

## Requirements - What do I need?
 * Python 3 – [How to install?](https://realpython.com/installing-python/)
 * ffmpeg – [How to install?](https://mityax.github.io/spdl.py-southpark-downloader/install-ffmpeg.html)<br>
    &rarr; ffmpeg is not required if you use spdl.py as a library and do not intend to use the built-in download function.

## Command line usage
The simplest possible command line usage is:

```python3 spdl.py all```

This will download all south park seasons in english language to the directory "./South Park".

To download only some parts of the south park series use a command like this:

```python3 spdl.py S01-S07,S08E2-S08E5,S10```

This example will download the full seasons 1 to 7 (including season 7), episodes 2 to 5 from season 8 and the full season 10.

More (optional) options are:

```
  -p PATH, --path PATH  Specify where to save downloaded episodes and how the
                        files are called. Directories that do not exist are
                        created automatically. '%s' is replaced with the
                        current season number, '%e' with the current episode
                        number, '%t' with the episode's title and '%g' with
                        the global episode number (e.g. "1803")
  -l LANGUAGE, --language LANGUAGE
                        Set the language for the downloads. The default
                        language is english (en). Supported languages are: en,
                        uk, es, de, se
  -q QUALITY, --quality QUALITY
                        The video quality to use for downloads. Either 'max',
                        'medium', 'min' or a resolution string like
                        '1920x1080' to use the closest matching resolution
                        that is available. Default: max
  -b FFMPEG_BINARY, --ffmpeg-binary FFMPEG_BINARY
                        Specify the path of the ffmpeg binary. Default on unix
                        is 'ffmpeg', on windows it's 'ffmpeg.exe'
  -t THREADS, --threads THREADS
                        Specify the maximum number of threads to download
                        video parts concurrently. Default: 4
  -f TEMPDIR, --tempdir TEMPDIR
                        Specify where to put temporary files. This option can
                        be useful for example if you do not have enough space
                        left on your harddrive and want to work on an external
                        drive.
  -v, --verbose         Give a more verbose output of what is currently
                        happening.
```

## Use as python library
To download all episodes in english use this self-explanatory code:

```python3
import spdl

southpark = spdl.SouthPark('en')

for season in southpark.get_all_seasons():
  for episode in season.episodes:
    print(f"Downloading season {episode.season} episode {episode.episode_number_in_season}...")
    episode.download()
```

The ```episode``` object contains all metadata of a south park episode:

```python3
import spdl

episode = spdl.SouthPark().get_season(20).episodes[0]

print(episode.id)  # => "1e607994-e3bc-4608-8562-e0af707aecd8"
print(episode.title)  # => "Member Berries"
print(episode.description)  # => "In the season 20 premiere episode, the National Anthem gets a reboot by an American Icon. (South Park S20, E01 2)"
print(episode.short_description)  # => "In the season 20 premiere episode, the National Anthem gets a reboot by an American Icon. (South Park S20, E01 2)"
print(episode.thumbnail)  # => "https://southparkstudios.mtvnimages.com/south-park/assets/season-20/2001/episodethumbnails/southpark_2001_5333x3000.jpg"
print(episode.date)  # => 1473904800 (unix timestamp; use the built-in python time module to work with this)
print(episode.episode_number)  # => "2001"
print(episode.season)  # => "20"
print(episode.episode_number_in_season)  # => "01"
print(episode.lang)  # => "en"
```

The ```Episode.download()``` method accepts multiple keyword arguments to customize downloading:

```python3
episode.download(

  # Specify where to save the downloaded episode. You may use any file extension
  # supported by ffmpeg but .mp4 is suggested if you care about file meta data
  filename = './South Park/My Downloaded Episode.mp4',

  # The quality of the downloads: 'max', 'medium', 'min' or something like '1920x1080'
  quality = 'max',

)
```

There are more options available, take a look at the [documentation](https://mityax.github.io/spdl.py-southpark-downloader/#spdl.Episode.download) for more information.

### Advanced usage: video stream handling
Each South Park episode consists of about 3-4 single video files. That's just how the South Park website works.
To get these videos do this:

```python3
import spdl

episode = spdl.SouthPark().get_season(20).episodes[0]  # => <Episode episodeId=1e607994-e3bc-4608-8562-e0af707aecd8 season=20 episode=01 title="Member Berries">

videos = episode.get_videos() # => [<spdl.Video object at 0x7f07fed01438>, ...]
```

Each of the videos is available in multiple different qualities. To get all video stream urls, call

```python3
streams = videos[0].get_streams()  # => [<Stream resolution=1280x720 url="...">, <Stream resolution=960x540 url="...">, ...]
```

and to automatically select a single one use

```python3
# possible stream selectors are 'max', 'medium', 'min' or a resolution string
# like '1280x720' to get the closest matching stream
stream = videos[0].get_stream('max')  # => <Stream resolution=1280x720 url="...">
```

Then, you can easily retrieve the stream data:

```python3
print(stream.resolution)  # => "1280x720"
print(stream.url)  # => "https://dlvrsvc.mtvnservices.com/api/playlist/..."
```
### Full API documentation
The full API documentation can be found [here](https://mityax.github.io/spdl.py-southpark-downloader/).
