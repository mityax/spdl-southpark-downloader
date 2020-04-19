# spdl.py-southpark-downloader
Download full south park seasons and episodes. Provides a command line interface and can also be imported as a python southpark library.

## Requirements - What do I need?
spdl.py is a Python 3 script. The only system requirement to download episodes is a working ffmpeg binary.
On most ubuntu-like systems a simple

```sudo apt install ffmpeg```

should be enough, if ffmpeg is not installed already. To install ffmpeg on other platforms, visit their (download site)[https://www.ffmpeg.org/download.html].
If you use spdl.py as a python library and do not want to use the built-in download function, you don't event need ffmpeg.

## Command line usage
The simplest possible command line usage is:

```python3 /spdl.py all```

This will download all south park seasons in english language to the directory "./South Park"

More options are:

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
```

## Usage as python library
To download all episodes in english use this self-explanatory code:

```
import spdl

southpark = spdl.SouthPark('en')

for season in southpark.get_all_seasons():
  for episode in season.episodes:
    print(f"Downloading season {episode.season} episode {episode.episode_number_in_season}...")
    episode.download()
```

The ```episode``` object contains all metadata of a south park episode:

```
import spdl

episode = spdl.SouthPark().get_season(20).episodes[0]

print(episode.id)  # => 1e607994-e3bc-4608-8562-e0af707aecd8
print(episode.title)  # => Member Berries
print(episode.description)  # => In the season 20 premiere episode, the National Anthem gets a reboot by an American Icon. (South Park S20, E01 2)
print(episode.short_description)  # => In the season 20 premiere episode, the National Anthem gets a reboot by an American Icon. (South Park S20, E01 2)
print(episode.thumbnail)  # => https://southparkstudios.mtvnimages.com/south-park/assets/season-20/2001/episodethumbnails/southpark_2001_5333x3000.jpg
print(episode.date)  # => 1473904800 (unix timestamp; use the built-in python time module to work with this)
print(episode.episode_number)  # => 2001
print(episode.season)  # => 20
print(episode.episode_number_in_season)  # => 01
print(episode.lang)  # => en
```

### Advanced usage: video stream handling
Each South Park episode consists of about 3-4 single video files. That's just how the South Park website works.
To get these videos do this:

```
import spdl

episode = spdl.SouthPark().get_season(20).episodes[0]
videos = episode.get_videos()
```

Each of the videos is available in multiple different qualities. To get all video stream urls, call

```
streams = videos[0].get_streams()
```

and to automatically select a single one use

```
stream = videos[0].get_stream('max')  # possible stream selectors are 'max', 'medium', 'min' or a resolution string like '1280x720' to get the closes matching stream
```

Then, you can easily retrieve the stream data:

```
print(stream.resolution)  # => 1280x720
print(stream.url)  # => https://dlvrsvc.mtvnservices.com/api/playlist/gsp.comedystor/com/sp/season-20/2001/acts/0/stream_1280x720_1197995.m3u8?tk=st=1587291688~exp=1587306088~acl=/api/playlist/gsp.comedystor/com/sp/season-20/2001/acts/0/stream_1280x720_1197995.m3u8*~hmac=5f9c3d1b0ae6f1d5e624a7539d8097876f19ceab7278bf972247803cfa14803a&account=southparkstudios.com&cdn=level3
```

### Full library documentation
<table summary="heading" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#7799ee">

<td valign="bottom">   
<font face="helvetica, arial" color="#ffffff">   
<big><big>**spdl**</big></big></font></td>

<td valign="bottom" align="right"><font face="helvetica, arial" color="#ffffff">[index](.)  
[/home/x/Projekte/spdl/spdl.py](file:/home/x/Projekte/spdl/spdl.py)</font></td>

</tr>

</tbody>

</table>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#aa55cc">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#ffffff"><big>**Modules**</big></font></td>

</tr>

<tr>

<td bgcolor="#aa55cc"></td>

<td> </td>

<td width="100%">

<table summary="list" width="100%">

<tbody>

<tr>

<td width="25%" valign="top">[atexit](atexit.html)  
[lxml.etree](lxml.etree.html)  
[json](json.html)  
</td>

<td width="25%" valign="top">[logging](logging.html)  
[os](os.html)  
[re](re.html)  
</td>

<td width="25%" valign="top">[shutil](shutil.html)  
[sys](sys.html)  
[tempfile](tempfile.html)  
</td>

<td width="25%" valign="top">[time](time.html)  
[urllib](urllib.html)  
</td>

</tr>

</tbody>

</table>

</td>

</tr>

</tbody>

</table>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#ee77aa">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#ffffff"><big>**Classes**</big></font></td>

</tr>

<tr>

<td bgcolor="#ee77aa"></td>

<td> </td>

<td width="100%">

<dl>

<dt><font face="helvetica, arial">[builtins.object](builtins.html#object)</font></dt>

<dd>

<dl>

<dt><font face="helvetica, arial">[Episode](spdl.html#Episode)</font></dt>

<dt><font face="helvetica, arial">[Season](spdl.html#Season)</font></dt>

<dt><font face="helvetica, arial">[SouthPark](spdl.html#SouthPark)</font></dt>

<dt><font face="helvetica, arial">[Stream](spdl.html#Stream)</font></dt>

<dt><font face="helvetica, arial">[Video](spdl.html#Video)</font></dt>

</dl>

</dd>

</dl>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#ffc8d8">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#000000"><a name="Episode">class **Episode**</a>([builtins.object](builtins.html#object))</font></td>

</tr>

<tr>

<td bgcolor="#ffc8d8"></td>

<td> </td>

<td width="100%">Methods defined here:  

<dl>

<dt><a name="Episode-__init__">**__init__**</a>(self, id:str, title:str, description:str, short_description:str, thumbnail:str, date:float, episode_number:str, season:Union[str, NoneType]=None, episode_number_in_season:Union[str, NoneType]=None, _lang:str='en')</dt>

<dd><tt>Initialize self.  See help(type(self)) for accurate signature.</tt></dd>

</dl>

<dl>

<dt><a name="Episode-__lt__">**__lt__**</a>(self, other)</dt>

<dd><tt>Return self<value.</tt></dd>

</dl>

<dl>

<dt><a name="Episode-__repr__">**__repr__**</a>(self)</dt>

<dd><tt>Return repr(self).</tt></dd>

</dl>

<dl>

<dt><a name="Episode-__str__">**__str__**</a>(self)</dt>

<dd><tt>Return str(self).</tt></dd>

</dl>

<dl>

<dt><a name="Episode-download">**download**</a>(self, filename:Union[str, NoneType]=None, quality:str='max', ffmpeg_executable:Union[str, NoneType]=None, max_threads:int=4)</dt>

<dd><tt>Downloads the episode to a file using a single thread. ffmpeg is required for this to work.  
:param filename: The file to save the download to. If it points to an existing directory, a new file is created in that directory following a simple name scheme and with avi extension.  
:param quality: The desired quality. Either 'max', 'medium', 'min', or a resolution like '1920x1080' (the closes matching resolution is taken in this case)  
:param ffmpeg_executable: The path to the ffmpeg executable, defaults to 'ffmpeg' on unix and 'ffmpeg.exe' on windows  
:param max_threads: The maximum number of downloads to perform concurrently.</tt></dd>

</dl>

<dl>

<dt><a name="Episode-get_videos">**get_videos**</a>(self) -> List[spdl.Video]</dt>

<dd><tt>Each south park episode consists of about 3-4 separate videos. This method returns a list of them.</tt></dd>

</dl>

* * *

Data descriptors defined here:  

<dl>

<dt>**__dict__**</dt>

<dd><tt>dictionary for instance variables (if defined)</tt></dd>

</dl>

<dl>

<dt>**__weakref__**</dt>

<dd><tt>list of weak references to the object (if defined)</tt></dd>

</dl>

</td>

</tr>

</tbody>

</table>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#ffc8d8">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#000000"><a name="Season">class **Season**</a>([builtins.object](builtins.html#object))</font></td>

</tr>

<tr>

<td bgcolor="#ffc8d8"></td>

<td> </td>

<td width="100%">Methods defined here:  

<dl>

<dt><a name="Season-__init__">**__init__**</a>(self, season_num:int, episodes:List[spdl.Episode])</dt>

<dd><tt>Initialize self.  See help(type(self)) for accurate signature.</tt></dd>

</dl>

<dl>

<dt><a name="Season-__repr__">**__repr__**</a>(self)</dt>

<dd><tt>Return repr(self).</tt></dd>

</dl>

<dl>

<dt><a name="Season-__str__">**__str__**</a>(self)</dt>

<dd><tt>Return str(self).</tt></dd>

</dl>

* * *

Data descriptors defined here:  

<dl>

<dt>**__dict__**</dt>

<dd><tt>dictionary for instance variables (if defined)</tt></dd>

</dl>

<dl>

<dt>**__weakref__**</dt>

<dd><tt>list of weak references to the object (if defined)</tt></dd>

</dl>

</td>

</tr>

</tbody>

</table>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#ffc8d8">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#000000"><a name="SouthPark">class **SouthPark**</a>([builtins.object](builtins.html#object))</font></td>

</tr>

<tr bgcolor="#ffc8d8">

<td rowspan="2"></td>

<td colspan="2"><tt>A simple South Park interface supporting downloads and advanced video stream management.  
 </tt></td>

</tr>

<tr>

<td> </td>

<td width="100%">Methods defined here:  

<dl>

<dt><a name="SouthPark-__init__">**__init__**</a>(self, lang:str='en')</dt>

<dd><tt>Initialize self.  See help(type(self)) for accurate signature.</tt></dd>

</dl>

<dl>

<dt><a name="SouthPark-get_all_seasons">**get_all_seasons**</a>(self) -> List[spdl.Season]</dt>

<dd><tt>Get all seasons available for the current language. This messuge performs a network request  
for each season to fetch the episode information. If you do not need this consider using `[get_season](#SouthPark-get_season)(str)`  
to get a specific season alongside `[get_season_numbers](#SouthPark-get_season_numbers)(str)` to get a list of all existing season numbers.  
:return: A list containing a [Season](#Season) [object](builtins.html#object) for each season</tt></dd>

</dl>

<dl>

<dt><a name="SouthPark-get_season">**get_season**</a>(self, season:int) -> spdl.Season</dt>

<dd><tt>Get a [Season](#Season) [object](builtins.html#object) for a specific south park season.  
:param season: The [Season](#Season)'s number (as int)</tt></dd>

</dl>

<dl>

<dt><a name="SouthPark-get_season_numbers">**get_season_numbers**</a>(self) -> List[int]</dt>

<dd><tt>Get a list of all season numbers of the current language.  
:return: A list containing the season numbers, as ints</tt></dd>

</dl>

* * *

Data descriptors defined here:  

<dl>

<dt>**__dict__**</dt>

<dd><tt>dictionary for instance variables (if defined)</tt></dd>

</dl>

<dl>

<dt>**__weakref__**</dt>

<dd><tt>list of weak references to the object (if defined)</tt></dd>

</dl>

</td>

</tr>

</tbody>

</table>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#ffc8d8">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#000000"><a name="Stream">class **Stream**</a>([builtins.object](builtins.html#object))</font></td>

</tr>

<tr>

<td bgcolor="#ffc8d8"></td>

<td> </td>

<td width="100%">Methods defined here:  

<dl>

<dt><a name="Stream-__init__">**__init__**</a>(self, resolution:str, url:str)</dt>

<dd><tt>Initialize self.  See help(type(self)) for accurate signature.</tt></dd>

</dl>

<dl>

<dt><a name="Stream-__lt__">**__lt__**</a>(self, other)</dt>

<dd><tt>Return self<value.</tt></dd>

</dl>

<dl>

<dt><a name="Stream-__repr__">**__repr__**</a>(self)</dt>

<dd><tt>Return repr(self).</tt></dd>

</dl>

<dl>

<dt><a name="Stream-__str__">**__str__**</a>(self)</dt>

<dd><tt>Return str(self).</tt></dd>

</dl>

* * *

Data descriptors defined here:  

<dl>

<dt>**__dict__**</dt>

<dd><tt>dictionary for instance variables (if defined)</tt></dd>

</dl>

<dl>

<dt>**__weakref__**</dt>

<dd><tt>list of weak references to the object (if defined)</tt></dd>

</dl>

</td>

</tr>

</tbody>

</table>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#ffc8d8">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#000000"><a name="Video">class **Video**</a>([builtins.object](builtins.html#object))</font></td>

</tr>

<tr>

<td bgcolor="#ffc8d8"></td>

<td> </td>

<td width="100%">Methods defined here:  

<dl>

<dt><a name="Video-__init__">**__init__**</a>(self, streams:List[str], duration:List[int], captions:str)</dt>

<dd><tt>Initialize self.  See help(type(self)) for accurate signature.</tt></dd>

</dl>

<dl>

<dt><a name="Video-get_play_data">**get_play_data**</a>(self) -> Tuple[str, str]</dt>

</dl>

<dl>

<dt><a name="Video-get_stream">**get_stream**</a>(self, quality:str='max') -> spdl.Stream</dt>

<dd><tt>Returns a single stream for this video.  
:param quality: The desired quality. Either 'max', 'medium', 'min', or a resolution like '1920x1080' (the closes matching resolution is taken in this case)  
:return: The [Stream](#Stream) [object](builtins.html#object)</tt></dd>

</dl>

<dl>

<dt><a name="Video-get_streams">**get_streams**</a>(self) -> List[spdl.Stream]</dt>

<dd><tt>Get a list of streams in different qualities for this [Video](#Video). The list is sorted by the  
stream quality in descending order, so that you can easily retrieve the highest quality stream  
using the first element.</tt></dd>

</dl>

* * *

Data descriptors defined here:  

<dl>

<dt>**__dict__**</dt>

<dd><tt>dictionary for instance variables (if defined)</tt></dd>

</dl>

<dl>

<dt>**__weakref__**</dt>

<dd><tt>list of weak references to the object (if defined)</tt></dd>

</dl>

* * *

Data and other attributes defined here:  

<dl>

<dt>**RTMP_STREAMS** = ['rtmpe://viacommtvstrmfs.fplive.net:1935/viacommtvstrm', 'rtmpe://cp75298.edgefcs.net/ondemand']</dt>

</dl>

</td>

</tr>

</tbody>

</table>

</td>

</tr>

</tbody>

</table>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#eeaa77">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#ffffff"><big>**Functions**</big></font></td>

</tr>

<tr>

<td bgcolor="#eeaa77"></td>

<td> </td>

<td width="100%">

<dl>

<dt><a name="-escape_filename">**escape_filename**</a>(string:str) -> str</dt>

<dd><tt>Escape a string to put it into a file name. This removes special chars from the string that  
are not supported by the filesystem.  
:param string: The string to escape  
:return: The escaped string</tt></dd>

</dl>

<dl>

<dt><a name="-http_get">**http_get**</a>(url:str, default:Any='') -> bytes</dt>

<dd><tt>Perform a simple HTTP GET request and return the response body as bytes.  
:param url: The url to fetch  
:param default: A default value to return on network errors.  
:return: The response body, as bytes</tt></dd>

</dl>

<dl>

<dt><a name="-parse_episode_string">**parse_episode_string**</a>(string:str) -> Tuple[int, int]</dt>

<dd><tt>Parses a string like "S04E12" into a tuple like (4, 12). Leading zeros are optional. If  
only a season number is supplied ("S04"), the second element in the tuple is None: (4, None)  
:param string: The season (and episode) string  
:return: The parsed tuple</tt></dd>

</dl>

<dl>

<dt><a name="-set_tempdir">**set_tempdir**</a>(dir:Union[str, NoneType]=None) -> str</dt>

<dd><tt>Set the directory to put temporary files. The files are deleted automatically when the script exits.  
:param dir: The temporary directory root</tt></dd>

</dl>

</td>

</tr>

</tbody>

</table>

<table summary="section" width="100%" cellspacing="0" cellpadding="2" border="0">

<tbody>

<tr bgcolor="#55aa55">

<td colspan="3" valign="bottom">   
<font face="helvetica, arial" color="#ffffff"><big>**Data**</big></font></td>

</tr>

<tr>

<td bgcolor="#55aa55"></td>

<td> </td>

<td width="100%">**ALL_SEASONS_URL** = {'de': 'https://www.southpark.de/alle-episoden', 'en': 'https://southpark.cc.com/all-episodes', 'es': 'https://southpark.cc.com/all-episodes', 'se': 'https://southparkstudios.nu', 'uk': 'https://southpark.cc.com/all-episodes'}  
**Any** = typing.Any  
**DOMAIN_REF** = {'de': 'www.southpark.de', 'en': 'southpark.cc.com', 'es': 'southpark.cc.com', 'se': 'southparkstudios.nu', 'uk': 'southpark.cc.com'}  
**DOMAIN_URL** = {'de': 'southpark.de', 'en': 'southparkstudios.com', 'es': 'southparkstudios.com', 'se': 'southparkstudios.nu', 'uk': 'southparkstudios.com'}  
**Optional** = typing.Optional  
**log** = <Logger spdl (WARNING)>  
**tempdir** = '/tmp/.spdl-1587296294.5946422'</td>

</tr>

</tbody>

</table>
