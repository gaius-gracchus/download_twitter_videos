#!/usr/bin/env bash

# list of hashtags to download videos from
declare -a hashtag_list=("ساحة_التحرير" "Baghdad" "Iraq" "IraqProtests" "IraqRevolution" "Save_the_Iraqi_people")

# infinite loop; perpetually collect tweet data
while true
do

  # loop over hashtags
  for hashtag in "${hashtag_list[@]}"
  do

    # execute python script for a hashtag until it terminates successfully
    until python download_twitter_videos.py --hashtag $hashtag
    do
      echo "Retried for hashtag "$hashtag
    done
  done

done
