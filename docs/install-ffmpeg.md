# How to install ffmpeg

You have two options to get ffmpeg working on your system. You can either [download a static build](#other) or you can properly install ffmpeg in your system to make it available for all programs. To do a full install, choose your platform here:

* [Unix (Ubuntu, Linux Mint, Debian)](#unix)
* [Mac OS X](#macosx)
* [Windows](#windows)
* [Other Platforms (Using Static Builds)](#other)

However, if you use spdl.py as a python library and do not want to use the built-in download function, you don't event need ffmpeg and you may just skip the installation.

## Installation on Unix <a name="unix" />
### Ubuntu and Linux Mint

```bash
$ sudo add-apt-repository ppa:mc3man/trusty-media
$ sudo apt-get update
$ sudo apt-get install ffmpeg
$ ffmpeg -version
```

### Debian
To install FFmpeg, first you need to add the following line to your /etc/apt/sources.list file. As per your distribution, change ‘<mydist>‘ with ‘stretch‘, ‘jessie‘, or ‘wheezy‘.

```
deb http://www.deb-multimedia.org <mydist> main non-free deb-src http://www.deb-multimedia.org <mydist> main non-free
```

Then update system package sources and install FFmpeg with the following commands.

```bash
$ sudo apt-get update
$ sudo apt-get install deb-multimedia-keyring
$ sudo apt-get update
$ sudo apt-get install ffmpeg
```

## Installation on Mac OS X <a name="macosx" />
The easiest way to install ffmpeg on Mac OS is using homebrew:

```bash
$ brew install ffmpeg
```

## Installation on Windows <a name="windows" />
1. Download a static build from [here](http://ffmpeg.zeranoe.com/builds/).
2. Use [7-Zip](http://7-zip.org/) to unpack it in the folder of your choice.
3. [Open a command prompt with administrator's rights](https://github.com/adaptlearning/adapt_authoring/wiki/Just-Enough-Command-Line-for-Installing).
    
    ***NOTE:** Use CMD.exe, do not use Powershell! The syntax for accessing environment variables is different from the command shown in Step 4 - running it in Powershell will overwrite your System PATH with a bad value.*
4. Run the command (see note below; in Win7 and Win10, you might want to use the Environmental Variables area of the Windows Control Panel to update PATH):
  
    ```cmd
    setx /M PATH "path\to\ffmpeg\bin;%PATH%"
    ```
    Do not run setx if you have more than 1024 characters in your system PATH variable. See [this post](https://superuser.com/questions/387619/overcoming-the-1024-character-limit-with-setx) on SuperUser that discusses alternatives. Be sure to alter the command so that path\to reflects the folder path from your root to ffmpeg\bin.

## Other Platforms (Using Static Builds) <a name="other" />
To install ffmpeg on other platforms, visit their [download site](https://www.ffmpeg.org/download.html).
You can download any ffmpeg binary from there that fits to your platform and save it anywhere on your computer. If it's not in your environment PATH just point spdl.py to the executeable by adding the ```--ffmpeg-binary``` option to the commandline like this:

```bash
$ python3 spdl.py all --ffmpeg-binary /path/to/your/downloaded/binary
```

Everything should work just fine now.
