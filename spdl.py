#!/usr/bin/env python3

import atexit
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional, Tuple, Dict, Any

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.ElementTree as etree
    except ImportError:
        try:
            import cElementTree as etree
        except ImportError:
            try:
                import elementtree.ElementTree as etree
            except ImportError:
                raise ImportError("Couldn't import ElementTree from any known place - please install lxml for python 3")

log = logging.getLogger('spdl')


def set_tempdir(dir: Optional[str] = None) -> str:
    """
    Set the directory to put temporary files. The files are deleted automatically when the script exits.
    :param dir: The temporary directory root
    """
    global tempdir
    tempdir = os.path.join(dir or tempfile.gettempdir(), f'.spdl-{time.time()}')
    if not os.path.isdir(tempdir):
        os.mkdir(tempdir)
    atexit.register(lambda: shutil.rmtree(tempdir))
    return tempdir


tempdir = set_tempdir()


DOMAIN_REF = {
    'en': "southpark.cc.com",  ## en
    'uk': "southpark.cc.com",  ## en uk
    'es': "southpark.cc.com",  ## es
    'de': "www.southpark.de",  ## de
    'se': "southparkstudios.nu"  ## se
}

DOMAIN_URL = {
    'en': "southparkstudios.com",  ## en
    'uk': "southparkstudios.com",  ## en uk
    'es': "southparkstudios.com",  ## es
    'de': "southpark.de",  ## de
    'se': "southparkstudios.nu"  ## se
}

ALL_SEASONS_URL = {  # TODO: only the german address is currently valid; correct the others
    'en': "https://southpark.cc.com/all-episodes",  ## en
    'uk': "https://southpark.cc.com/all-episodes",  ## en uk
    'es': "https://southpark.cc.com/all-episodes",  ## es
    'de': "https://www.southpark.de/alle-episoden",  ## de
    'se': "https://southparkstudios.nu"  ## se
}


class Stream(object):
    def __init__(self, resolution: str, url: str):
        self.url: str = url
        """The url of the stream."""
        self.resolution: str = resolution
        """The resolution of the stream as a string in the format \"1920x1080\""""

    def __str__(self):
        return f"<{type(self).__name__} at {id(self)} resolution={self.resolution} url=\"{self.url}\">"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return int(self.resolution.split("x")[0]) < int(other.resolution.split("x")[0])


class Video:
    RTMP_STREAMS = [
        "rtmpe://viacommtvstrmfs.fplive.net:1935/viacommtvstrm",
        "rtmpe://cp75298.edgefcs.net/ondemand"
    ]

    def __init__(self, streams: List[str], duration: List[int], captions: str):
        self.__streams = streams
        self.duration: List[int] = duration
        """The duration of the video"""
        self.captions: str = captions
        """Sub-titles for the video"""

    def __rtmp_streams(self, index: int = 0) -> str:
        return self.RTMP_STREAMS[index]

    def get_streams(self) -> List[Stream]:
        """
        Get a list of streams in different qualities for this Video. The list is sorted by the
        stream quality in descending order, so that you can easily retrieve the highest quality stream
        using the first element.
        """
        p = http_get(self.get_play_data()[1])
        streams = []
        curr_res = None
        for line in p.splitlines():
            if line.startswith(b"#EXT-X-STREAM-INF:"):
                curr_res = re.search(rb'RESOLUTION=(\d+x\d+)', line).group(1)
            elif not line.startswith(b"#") and line.strip():
                streams.append(Stream(curr_res.decode("utf-8"), line.decode("utf-8")))
        return sorted(streams, reverse=True)

    def get_stream(self, quality: str = 'max') -> Stream:
        """
        Returns a single stream for this video.
        :param quality: The desired quality. Either 'max', 'medium', 'min', or a resolution like '1920x1080' (the closes matching resolution is taken in this case)
        :return: The Stream object
        """
        streams = self.get_streams()
        if quality == 'max':
            return streams[0]
        elif quality == 'min':
            return streams[-1]
        elif quality == 'medium':
            return streams[len(streams) // 2]
        elif re.match(r"\d+x\d+$", quality):
            q = int(quality.split("x")[0]) * int(quality.split("x")[0])
            streams = sorted(streams,
                             key=lambda s: abs(q - int(s.resolution.split("x")[0]) * int(s.resolution.split("x")[0])))
            return streams[0]
        else:
            raise ValueError(
                f"Invalid quality string: \"{quality}\". Use one of 'max', 'medium', 'min' or a resolution like '1920x1080'")

    def get_play_data(self) -> Tuple[str, str]:
        ## High quality is the last stream  (-1)
        vqual = -1
        rtmp = self.__streams[vqual]
        playpath = ""
        if "http" not in rtmp:
            if "viacomccstrm" in self.__streams[vqual]:
                playpath = "mp4:{0}".format(self.__streams[vqual].split('viacomccstrm/')[1])
                rtmp = self.__rtmp_streams()
            elif "cp9950.edgefcs.net" in self.__streams[vqual]:
                playpath = "mp4:{0}".format(self.__streams[vqual].split('mtvnorigin/')[1])
                rtmp = self.__rtmp_streams()
        return playpath, rtmp


class Episode:
    def __init__(self, id: str, title: str, description: str, short_description: str, thumbnail: str, date: float,
                 episode_number: str, season: Optional[str] = None,
                 episode_number_in_season: Optional[str] = None, _lang: str = 'en'):
        self.id: str = id
        """The south park intern uid of the episode"""
        self.title: str = title
        """The title of the episode"""
        self.description: str = description
        """The description of the episode"""
        self.short_description: str = short_description
        """A short description of the episode"""
        self.thumbnail: str = thumbnail
        """A URL to the thumbnail image of the episode"""
        self.date: float = date
        """The date of the episode as a unix timestamp"""
        self.episode_number: str = episode_number
        """The global episode number, e.g. "1908" or "2001\""""
        self.season: str = season
        """The number of the season the episode belongs to"""
        self.episode_number_in_season: str = episode_number_in_season
        """The episode number relative to it's season, e.g. "06\""""
        self.lang: str = _lang
        """The language of the episode, inherited from the SouthPark constructor"""

    def get_videos(self) -> List[Video]:
        """
        Each south park episode consists of about 3-4 separate videos. This method returns a list of them.
        """
        return [self.__get_video(m) for m in self.__get_mediagen()]

    def download(self, filename: Optional[str] = None, quality: str = 'max', ffmpeg_executable: Optional[str] = None, max_threads: int = 4):
        """
        Downloads the episode to a file using a single thread. ffmpeg is required for this to work.
        :param filename: The file to save the download to. If it points to an existing directory, a new file is created in that directory following a simple name scheme and with .mp4 extension.
        :param quality: The desired quality. Either 'max', 'medium', 'min', or a resolution like '1920x1080' (the closes matching resolution is taken in this case)
        :param ffmpeg_executable: The path to the ffmpeg executable, defaults to 'ffmpeg' on unix and 'ffmpeg.exe' on windows
        :param max_threads: The maximum number of downloads to perform concurrently.
        """

        if filename is None:

            filename = f'S{self.season}E{self.episode_number_in_season} - {escape_filename(self.title)}.mp4'
        elif os.path.isdir(filename):
            filename = os.path.join(filename, f'S{self.season}E{self.episode_number_in_season} - {escape_filename(self.title)}.mp4')

        if ffmpeg_executable is None:
            ffmpeg_executable = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'

        log.info("Downloading Episode \"%s\" (S%sE%s) to %s...", self.title, self.season, self.episode_number_in_season,
                 filename)

        videos = self.get_videos()

        fns = []
        with ThreadPoolExecutor(max_workers=max_threads) as e:
            for i, vid in enumerate(videos):
                stream = vid.get_stream(quality=quality)
                fn = os.path.join(tempdir, f"{self.id}--{i}.ts")
                fns.append(fn)
                log.info("Initiated download of stream #%s of %s...", i, len(videos))
                e.submit(lambda: subprocess.Popen([ffmpeg_executable, '-loglevel', 'warning', '-y', '-i', stream.url, '-codec', 'copy', fn], stdin=subprocess.PIPE).wait())

        log.info("Merging downloaded streams...")
        metadata = []
        for k, v in {
                        "title": f"{self.title} (S{self.season} E{self.episode_number_in_season})",
                        "description": self.description,
                        "comment": self.description,
                        "year": time.localtime(self.date).tm_year,
                        "track": self.episode_number_in_season,
                        "synopsis": self.short_description,
                        "show": "South Park",
                        "episode_id": self.episode_number,
                        "album": self.season,
                        "author": "The South Park Team"
                    }.items():
            metadata.append("-metadata")
            metadata.append(f'{k}={escape_string(str(v))}')
        subprocess.Popen([ffmpeg_executable, '-loglevel', 'warning', '-y',  '-i', f'concat:{"|".join(fns)}'] + metadata + ['-c:v', 'copy', f'{filename}']).wait()

        log.info("Cleaning up...")
        for f in fns:
            os.remove(f)

        log.info("Download of Episode \"%s\" (S%sE%s) done.", self.title, self.season, self.episode_number_in_season)

    def __get_video(self, mediagen: str) -> Video:
        if self.lang != "de":
            mediagen = mediagen.replace('device={device}', 'device=Android&deviceOsVersion=4.4.4&acceptMethods=hls')
        else:
            mediagen = mediagen.replace('device={device}', 'acceptMethods=hls')
        xml = http_get(mediagen)
        root = etree.fromstring(xml)
        rtmpe = []
        duration = []
        captions = ""
        if sys.version_info >= (2, 7):
            for item in root.iter('src'):
                if item.text != None and not "intros" in item.text:
                    if self.lang == "es":
                        rtmpe.append(item.text)
                    elif not "acts/es" in item.text:
                        rtmpe.append(item.text)
            for item in root.iter('rendition'):
                if item.attrib['duration'] != None:
                    duration.append(int(item.attrib['duration']))
            for item in root.iter('typographic'):
                if item.attrib['src'] != None and item.attrib['format'] == "vtt":
                    captions = item.attrib['src']
        else:
            for item in root.getiterator('src'):
                if item.text != None and not "intros" in item.text:
                    if self.lang == "es":
                        rtmpe.append(item.text)
                    elif not "acts/es" in item.text:
                        rtmpe.append(item.text)
            for item in root.getiterator('rendition'):
                if item.attrib['duration'] != None:
                    duration.append(int(item.attrib['duration']))
            for item in root.getiterator('typographic'):
                if item.attrib['src'] != None and item.attrib['format'] == "vtt":
                    captions = item.attrib['src']
        return Video(rtmpe, duration, captions)

    def __get_mediagen(self) -> List[str]:
        mediagen = []
        comp = self.__mediagen_url()
        feed = http_get(comp)
        if self.lang == "se":
            jsondata = json.loads(feed)
            for media in jsondata["feed"]["items"]:
                mediagen.append(media["group"]["content"])
        else:
            root = etree.fromstring(feed)
            if sys.version_info >= (2, 7):
                for item in root.iter('{http://search.yahoo.com/mrss/}content'):
                    if item.attrib['url'] is not None:
                        mediagen.append(urllib.parse.unquote(item.attrib['url']))
            else:
                for item in root.getiterator('{http://search.yahoo.com/mrss/}content'):
                    if item.attrib['url'] is not None:
                        mediagen.append(urllib.parse.unquote(item.attrib['url']))
        return mediagen

    def __mediagen_url(self) -> str:
        if self.lang == "se":
            return "https://media.mtvnservices.com/pmt/e1/access/index.html?uri=mgid:arc:episode:{0}:{1}&configtype=edge".format(
                DOMAIN_URL[self.lang], self.id)
        return f"https://{DOMAIN_REF[self.lang]}/feeds/video-player/mrss/mgid:arc:episode:{DOMAIN_URL[self.lang]}:{self.id}?lang={self.lang.upper()}"

    def __str__(self):
        return f"<{type(self).__name__} at {id(self)} episodeId={self.id} season={self.season} episode={self.episode_number_in_season} title=\"{self.title}\">"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return int(self.episode_number) < int(other.episode_number)


class Season:
    def __init__(self, season_num: int, episodes: List[Episode]):
        self.season_num: int = season_num
        """The season number"""
        self.episodes: List[Episode] = episodes
        """A list of all episodes in the season"""

    def __str__(self):
        return f"<{type(self).__name__} at {id(self)} season={self.season_num} episodes={len(self.episodes)}>"

    def __repr__(self):
        return str(self)


class SouthPark:
    """
    A simple South Park interface supporting downloads and advanced video stream management.
    """

    def __init__(self, lang: str = 'en'):
        if lang not in DOMAIN_URL:
            raise ValueError(f"Unsupported language: {lang}. Supported languages are: {', '.join(DOMAIN_URL.keys())}")
        self.lang = lang.lower()

    def get_season_numbers(self) -> List[int]:
        """
        Get a list of all season numbers of the current language.
        :return: A list containing the season numbers, as ints
        """
        resp = http_get(ALL_SEASONS_URL[self.lang])
        return sorted(set([int(x.group(1)) for x in re.finditer(r'data-value="season-(\d+)"', resp)])) or list(range(24))

    def get_all_seasons(self) -> List[Season]:
        """
        Get all seasons available for the current language. This messuge performs a network request
        for each season to fetch the episode information. If you do not need this consider using `get_season(str)`
        to get a specific season alongside `get_season_numbers(str)` to get a list of all existing season numbers.
        :return: A list containing a Season object for each season
        """
        for season in self.get_season_numbers():
            yield self.get_season(season)

    def get_season(self, season: int) -> Season:
        """
        Get a Season object for a specific south park season.
        :param season: The Season's number (as int)
        """
        if self.lang == "de":
            url = f"https://www.southpark.de/feeds/carousel/video/e3748950-6c2a-4201-8e45-89e255c06df1/30/1/json/!airdate/season-{season}"
        elif self.lang == "se" and season < 23:  # SE doesn't have the 23rd season.
            url = f"https://www.southparkstudios.nu/feeds/carousel/video/9bbbbea3-a853-4f1c-b5cf-dc6edb9d4c00/30/1/json/!airdate/season-{season}"
        elif self.lang == "uk":
            url = f"https://www.southparkstudios.co.uk/feeds/carousel/video/02ea1fb4-2e7c-45e2-ad42-ec8a04778e64/30/1/json/!airdate/season-{season}"
        # cc.com is the ony one with jsons so descriptions will be in english
        else:
            url = f"https://southpark.cc.com/feeds/carousel/video/06bb4aa7-9917-4b6a-ae93-5ed7be79556a/30/1/json/!airdate/season-{season}?lang={self.lang}"

        season_data = json.loads(http_get(url))

        episodes = []
        for e in season_data["results"]:
            episodes.append(Episode(
                id=e.get("itemId").strip(),
                title=e.get("title").strip(),
                description=e.get("description").strip(),
                short_description=e.get("shortDescription").strip(),
                thumbnail=e.get("images").strip(),
                date=int(e.get("originalAirDate", 0).strip()),
                episode_number=e.get("episodeNumber").strip(),
                episode_number_in_season=e.get("episodeNumber", "0")[-2:].strip(),
                season=e.get("episodeNumber", "0")[:2].strip(),
                _lang=self.lang
            ))

        return Season(season, episodes)

    def __carousel(self, video_id: Optional[str] = None) -> Dict:
        if self.lang == 'de':
            url = f"https://www.southpark.de/feeds/carousel/video/{video_id or 'e3748950-6c2a-4201-8e45-89e255c06df1'}/30/1/json"
        elif self.lang == 'se':
            url = f"https://www.southparkstudios.nu/feeds/carousel/wiki/{video_id or '3fb9ffcb-1f70-42ed-907d-9171091a28f4'}/12/1/json"
        elif self.lang == 'uk':
            url = f"https://www.southparkstudios.co.uk/feeds/carousel/wiki/{video_id or '4d56eb84-60d9-417e-9550-31bbfa1e7fb9'}/12/1/json"
        else:
            url = f"https://southpark.cc.com/feeds/carousel/video/{video_id or '2b6c5ab4-d717-4e84-9143-918793a3b636'}/14/2/json/!airdate/?lang={self.lang.upper()}"
        return json.loads(http_get(url))


def http_get(url: str, default: Any = '') -> bytes:
    """
    Perform a simple HTTP GET request and return the response body as bytes.
    :param url: The url to fetch
    :param default: A default value to return on network errors.
    :return: The response body, as bytes
    """
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.read()
    except:
        return default


def escape_filename(string: str) -> str:
    """
    Escape a string to put it into a file name. This removes special chars from the string that
    are not supported by the filesystem.
    :param string: The string to escape
    :return: The escaped string
    """
    return "".join(x if (x.isalnum() or x in "._- ") else '_' for x in string)


def escape_string(string: str) -> str:
    """
    Escapes a string so it can be passed via a command line argument
    :param string:  Th estring to escape
    :return: The escaped string
    """

    return string.replace('"', '\"').replace("\n", "\\n").replace("\r", "\\r")


def parse_episode_string(string: str) -> Tuple[int, int]:
    """
    Parses a string like "S04E12" into a tuple like (4, 12). Leading zeros are optional. If
    only a season number is supplied ("S04"), the second element in the tuple is None: (4, None)
    :param string: The season (and episode) string
    :return: The parsed tuple
    """
    m = re.match(r'S(\d+)(?:E(\d+))?', string.upper())
    if m:
        return int(m.group(1)), (int(m.group(2)) if m.group(2) else None)
    raise ValueError(f"Invalid season/episode selector: \"{string}\". Valid examples: 'S01' or 'S01E03'")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(os.path.basename(__file__), description="Download South Park Seasons or Episodes")
    parser.add_argument('what',
                        help="Specify what to download. Examples: 'all', 'S01', 'S01E02', 'S01-S07', 'S01,S02-S04,S05E01-S05E04'")
    parser.add_argument('-p', '--path', default='South Park/Season %s/%e - %t.mp4',
                        help=f"Specify where to save downloaded episodes and how the files are called. Directories that do not exist are created automatically. '%%s' is replaced with the current season number, '%%e' with the current episode number, '%%t' with the episode's title and '%%g' with the global episode number (e.g. \"1803\")")
    parser.add_argument('-l', '--language', default='en',
                        help=f"Set the language for the downloads. The default language is english (en). Supported languages are: {', '.join(DOMAIN_URL.keys())}")
    parser.add_argument('-q', '--quality', default='max',
                        help="The video quality to use for downloads. Either 'max', 'medium', 'min' or a resolution string like '1920x1080' to use the closest matching resolution that is available. Default: max")
    parser.add_argument('-b', "--ffmpeg-binary", default=None,
                        help="Specify the path of the ffmpeg binary. Default on unix is 'ffmpeg', on windows it's 'ffmpeg.exe'")
    parser.add_argument('-t', '--threads', default=4, type=int,
                        help="Specify the maximum number of threads to download video parts concurrently. Default: 4")
    parser.add_argument('-f', '--tempdir', default=tempdir,
                        help="Specify where to put temporary files. This option can be useful for example if you do not have enough space left on your harddrive and want to work on an external drive.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Give a more verbose output of what is currently happening.")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    s = SouthPark(args.language)

    print("Collecting episodes to download...")
    to_download = []
    if args.what == 'all':
        for season in s.get_all_seasons():
            for e in season.episodes:
                to_download.append(e)
    else:
        for el in map(str.strip, args.what.split(",")):
            if '-' in el:
                if el.count('-') > 1:
                    raise ValueError(f"Invalid parameter: {el} in {args.what}")
                start, end = map(parse_episode_string, map(str.strip, el.split("-", 1)))
                for i in range(start[0], end[0] + 1):
                    season = s.get_season(i)
                    for e in season.episodes:
                        if start[1] is not None and i == start[0] and int(e.episode_number_in_season) < start[1] \
                                or end[1] is not None and i == end[0] and int(e.episode_number_in_season) > end[1]:
                            continue
                        to_download.append(e)
            else:
                season, episode = parse_episode_string(el)
                if episode is not None:
                    for e in s.get_season(season).episodes:
                        if int(e.episode_number_in_season) == episode:
                            to_download.append(e)
                            break
                    else:
                        raise ValueError(f"Season {season} Episode {episode} does not exist.")
                else:
                    for e in s.get_season(season).episodes:
                        to_download.append(e)

    to_download.sort()

    print(f"Downloading {len(to_download)} episode(s) from {len(set(x.season for x in to_download))} season(s).")
    print(f"Language: {args.language}")
    print(f"Quality:  {args.quality}")
    print(f"Save to:  {args.path}")

    if input("Continue? [y/n] ") in ["n", "no", "abort", "exit", "stop", "cancel"]:
        print("Aborted by user.")
        exit()

    if os.path.isdir(args.path):
        args.path = os.path.join(args.path, 'Season %s/%e - %t.mp4')
    if args.tempdir != tempdir:
        set_tempdir(args.tempdir)

    for i, e in enumerate(to_download):
        path = os.path.realpath(
            args.path.replace("%s", e.season).replace("%e", e.episode_number_in_season).replace("%g", e.episode_number).replace("%t", escape_filename(e.title)))
        os.makedirs(os.path.dirname(path), exist_ok=True)

        print(f"Downloading season {e.season} episode {e.episode_number_in_season} - {e.title}...")
        log.debug("Saving to: %s", path)
        try:
            e.download(path, quality=args.quality, ffmpeg_executable=args.ffmpeg_binary, max_threads=args.threads)
        except KeyboardInterrupt:
            time.sleep(0.5)
            if input(f"Press return to skip only this download (S{e.season} E{e.episode_number_in_season}) or enter 'exit' to cancel all remaining downloads.") in ('exit', 'e', 'all'):
                print(f"Downloaded {i} episode(s) of {len(to_download)} ({round(i * 100. / len(to_download), 1)}%).")
                print("Aborted by user.")
                exit()
            if os.path.isfile(path):
                os.remove(path)
            print(f"Cancelled download of season {e.season} episode {e.episode_number_in_season} - {e.title}")

    print("All done.")
