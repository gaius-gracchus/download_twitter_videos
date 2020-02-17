# Download Twitter videos

This directory contains scripts for automatically downloading all videos from Twitter that contain one or more of a list of specified hashtags.
The Python script ``download_twitter_videos.py`` downloads videos for a single hashtag. The bash script ``runner.sh`` downloads videos for a specified list of hashtags py calling 
the Python script, and runs perpetually, i.e. downloads new videos as they are generated.

The *runner* script currently only works on Unix-like operating systems, so if you want to perpetually download Twitter videos on Windows, you need to either
install the [Windows Subsystem for Linux][wsl], write a .bat that mimics the behavior of the bash script, or get me to write such a .bat file. 

To run the Python script, you need to have Twitter Developer credentials, which you can get [here][twitter-dev]. 
Either copy and paste your Twitter developer credentials in lines 39-42 of ``download_twitter_videos.py``, or save them as environment variables in your ``~/.bashrc``.

To specify a list of hashtags to download, modify line 4 of ``runner.sh`` with a space-separated list of double-quoted hashtags.

To set the initial date (i.e. download all videos from tweets created between the current date and the initial date), modify line 48 of ``download_twitter_videos.py``.

An example of the script's output can be see on my post on [the Internet Archive][internet-archive].

[twitter-dev]: https://developer.twitter.com/en/apply-for-access.html
[internet-archive]: https://archive.org/details/savetheiraqipeople
[wsl]: https://docs.microsoft.com/en-us/windows/wsl/install-win10