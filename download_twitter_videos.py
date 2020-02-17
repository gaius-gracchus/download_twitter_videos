# -*- coding: UTF-8 -*-

"""Download all videos from tweets containing a given hashtag, since a
specified date.
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import os
import csv
import argparse
from datetime import datetime as dt

import numpy as np
import tweepy
import pandas as pd
import requests

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# parse command line arguments for hashtag to download videos of
parser = argparse.ArgumentParser( )
parser.add_argument(
  '--hashtag',
  help = 'hashtag of videos to be downloaded',
  type = str )

args = parser.parse_args( )
hashtag = args.hashtag

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# Twitter API credentials
# (this won't work unless you have Twitter Developer access)
# I saved my tokens as environment variables so I can upload this to
# GitHub without worrying about the security of my API credentials. If you're
# not planning on using internet-based version control, you can just paste your
# API credentials here.
consumer_key = os.getenv( 'TWITTER_CONSUMER_KEY' )
consumer_secret = os.getenv( 'TWITTER_CONSUMER_SECRET' )
access_token = os.getenv( 'TWITTER_ACCESS_TOKEN' )
access_token_secret = os.getenv( 'TWITTER_ACCESS_TOKEN_SECRET' )

# date format
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# starting date (i.e. download videos from tweets since this date)
initial_start_date = "2019-10-01 01:01:01"

# name of csv file to write tweet data to, for a given hashtag
file_name = f'{hashtag}.csv'

# name of csv file to write tweet data to, for a all hashtags
manifest_name = 'manifest.csv'

# if earliest tweet is not within `time_leeway` seconds of `initial_start_date`,
# we assume the previous run failed to complete
time_leeway = 2 * 60 * 60

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_timestamp( s ):

  """Extract the Unix epoch timestamp from a tweet's `created_at` field.

  Parameters
  ----------
  s : str
    Datetime string consistent with `DATE_FORMAT`, e.g. `2019-10-01 01:01:01`.

  Returns
  -------
  float
    Unix epoch (seconds since 1 January 1970) corresponding to the input
    datetime string `s`, e.g. `1569909661.0`
  """

  return dt.strptime( s, DATE_FORMAT ).timestamp( )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_first_last_datetimes( df ):

  """Extract the least and most recent datetimes from a Pandas DataFrame of a
  CSV file.

  Parameters
  ----------
  df : pandas.DataFrame
    DataFrame of a hashtag CSV file; must contain column named
    `tweet.created_at`.

  Returns
  -------
  dtmin : str
    Least recent datetime string contained in `df`.
  dtmax : str
    Most recent datetime string contained in `df`.
  """

  timestamps = df[ 'tweet.created_at' ].apply( get_timestamp )

  idxmin = timestamps.idxmin( )
  idxmax = timestamps.idxmax( )

  dtmin = df.loc[ idxmin ][ 'tweet.created_at' ]
  dtmax = df.loc[ idxmax ][ 'tweet.created_at' ]

  return dtmin, dtmax

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_video_url( tweet ):

  """If a tweet contains a video, return the video url.

  Parameters
  ----------
  tweet : tweepy.Status
    TweePy Status object containing information about a single tweet.

  Returns
  -------
  url : str or None
    If tweet contains a video, string of url of tht video.
    If tweet doesn't contain video, None.

  """

  bitrates = [ ]

  try:

    # select variant with highest bitrate
    variants = tweet.extended_entities['media'][0]['video_info']['variants']
    for variant in variants:
      bitrates.append( variant.get('bitrate', 0 ) )
    bitrates = np.asarray( bitrates )
    idx = np.argmax( bitrates )

    url = tweet.extended_entities['media'][0]['video_info']['variants'][idx]['url']
  except:
    url = None

  return url

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

  # create output directory of hashtag name if it doesn't exist already
  os.makedirs( hashtag, exist_ok = True )

  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  api = tweepy.API(auth,wait_on_rate_limit=True)

  # create files and initialize list of already-downloaded urls
  #---------------------------------------------------------------------------#

  # initialize list of URLs; initializing with None so we don't have to worry
  # about downloading nonexistant video urls.
  urls_list = [None]

  # timestamp of initial_start_date
  initial_start_timestamp = get_timestamp( s = initial_start_date )

  # if manifest csv file exists, copy list of already-downloaded video urls
  if os.path.isfile(manifest_name):

    df = pd.read_csv( manifest_name )
    urls_list.extend( list( df['video_url']) )

  # if manifest csv file doesn't exist, create it and write header
  else:
    with open(manifest_name, 'w') as f:
      f.write('tweet.id,tweet.created_at,tweet.text,video_url,video_name,hashtag\n')

  # if hashtag csv file exists, copy list of already-downloaded video urls
  if os.path.isfile(file_name):

    df = pd.read_csv( file_name )
    urls_list.extend( list( df['video_url']) )

    # determine time range to colelct tweets based on the previously collected
    # tweets.
    dtmin, dtmax = get_first_last_datetimes( df = df )

    min_timestamp = dt.strptime( dtmin, DATE_FORMAT ).timestamp()

    # we want to download
    # videos from all tweets generated between the most recent datetime in
    # the csv and now.

    since = dtmax

  # if hashtag csv file doesn't exist, create it and write header
  else:
    with open(file_name, 'w') as f:
      f.write('tweet.id,tweet.created_at,tweet.text,video_url,video_name\n')

    since = initial_start_date

  # TweePy's cursor doesn't seem to support sub-date information (e.g.
  # `2019-10-01` works, not `2019-10-01 01:01:01`.)
  since = since[:-9]

  # print information about current working hashtag
  print('')
  print('hashtag: ', hashtag)
  print('current time: ', dt.strftime( dt.now(), DATE_FORMAT ))
  print('since: ', since)
  print('')

  #---------------------------------------------------------------------------#

  # open/create a hashtag csv file to append data to
  hashtag_csv_file = open(file_name, 'a')
  hashtag_csv_writer = csv.writer(hashtag_csv_file)

  # open/create a manifest csv file to append data to
  manifest_csv_file = open(manifest_name, 'a')
  manifest_csv_writer = csv.writer(manifest_csv_file)

  # loop over all tweets since specified start_date and containing hashtag
  for tweet in tweepy.Cursor(
    api.search,
    q = hashtag,
    count = 100,
    include_entities = True,
    since = since ).items( ):

    # extract url from tweet, if it contains a video
    url = get_video_url( tweet )

    # check to make sure we haven't already downloaded the video for the given
    # url
    if url not in urls_list:

      urls_list.append( url )

      # video GET request
      r = requests.get( url )

      # file name to write video to
      fname = os.path.join( hashtag, url.split('/')[-1] )

      # printing information about each video
      print('')
      print('current time: ', dt.strftime( dt.now(), DATE_FORMAT ))
      print('hashtag: ', hashtag)
      print('response: ', r.status_code)
      print('tweet created time: ', tweet.created_at)
      print('video url: ', url)
      print('file name: ', fname)

      # write video to file
      with open(fname, 'wb') as f:
        f.write( r.content )

      # write tweet data to hashtag csv file
      hashtag_csv_writer.writerow([
        str(tweet.id),
        tweet.created_at,
        tweet.text.encode('utf-8'),
        url,
        fname ] )

      # write tweet data to manifest csv file
      manifest_csv_writer.writerow([
        str(tweet.id),
        tweet.created_at,
        tweet.text.encode('utf-8'),
        url,
        fname,
        hashtag ] )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#