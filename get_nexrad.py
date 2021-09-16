#! /usr/bin/env python3
#
# get_nexrad.py
#
# Useage:
#   conda activate nexrad-aws [s3fs install]
#   python get_nexrad.py -s 202005231200 -e 202005240305 -r KLOT -p /path/to/output/
#
# Output:
#   Level II msg31 archived nexrad files downloaded from AWS.
#

import sys
import re

from datetime import datetime, timedelta
import argparse
import numpy as np
from collections import defaultdict
import itertools

import s3fs

# RegEx string. Search pattern is SSSS/SSSS########_######
regex_string = "([\w]{4}/[\w]{4}[\d]{8}_[\d]{6})"

def grab_data(start_time, end_time, radar_id, local_path=None):
    """
    Parameters
    ----------
    start_time : int
        Initial time for data. Form is YYYYMMDDHHMM
    end_time : int
        End time for data. Form is YYYYMMDDHHMM
    radar_id : str
        4-digit radar identifier [KLOT, KDVN, KFWS, etc.]
    local_path : str
        Path to download files to. Must have write permissions.

    Other Parameters
    ----------------

    Returns
    -------
    None. Files downloaded to local system.

    """
    radar_id = radar_id.upper()
    fs = s3fs.S3FileSystem(anon=True)

    if local_path is None: local_path = "./"

    # Determine the date directories we'll need to search through on the AWS.
    # Individual days are stored as Julian Dates, so take care of that here.
    dt_start = datetime.strptime(start_time, '%Y-%m-%d/%H%M')
    dt_end = datetime.strptime(end_time, '%Y-%m-%d/%H%M')
    if dt_start > dt_end:
        print("Start and end dates are out of order.")
        sys.exit(1)
    delta = dt_end - dt_start

    # Loop through the data structure and find file names
    head = 'noaa-nexrad-level2/'

    #n_hours = len(time_dict['years'])
    files = []
    for i in range(delta.days + 2):
        date = dt_start + timedelta(days=i)
        tail = "%s/%s/%s/%s" % (date.year,
                                str(date.month).zfill(2),
                                str(date.day).zfill(2),
                                radar_id)
        listing = fs.ls(head + tail)
        files.append(listing)
    # Concatenate the list of files and purge the end-of-hour MDM files
    files = list(itertools.chain.from_iterable(files))
    files = [i for i in files if "_MDM" not in i]

    downloads = defaultdict(list)
    download_size = 0.
    for f in files:
        short_name = re.findall(regex_string,f)
        if len(short_name) == 1:
            short_name = short_name[0][5:]
            time_info = short_name[4:]
            scan_dt = datetime.strptime(time_info, '%Y%m%d_%H%M%S')

            if dt_start <= scan_dt <= dt_end:
                downloads[f] = local_path + '/' + short_name

                # Save off file size information
                download_size += fs.info(f)['Size']

    # Query user if they'd like to continue with this download based on expected
    # download size
    for key in downloads.keys():
        print(key)
    print("==>Number of requested files: ", len(downloads.keys()))
    str1 = "==>Requested download is approximately: "
    print(str1, round(download_size / 1000000.), " MB")
    print("==>Files will be downloaded to: ", local_path, " Continue? [y|n]")
    resp = input()

    # Continue on to download step?
    if resp == 'y':
        for f in downloads.keys():
            print("Downloading: ", downloads[f])
            fs.get(f, downloads[f])
    else:
        print("==================")
        print("===  Goodbye!  ===")
        print("==================")
        sys.exit(0)

    return

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--start-time', dest='start_time', help="First scan time [YYYY-MM-DD/HHmm]")
    ap.add_argument('-e', '--end_time', dest='end_time', help="Last scan time [YYYY-MM-DD/HHmm]")
    ap.add_argument('-r', '--radar_id', dest='radar_id', help="4-letter radar identifier [e.g. KLOT]")
    ap.add_argument('-p', '--local-path', dest='local_path', help="Path to store netCDF files")
    args = ap.parse_args()
    np.seterr(all='ignore')

    grab_data(args.start_time,
              args.end_time,
              args.radar_id,
              local_path = args.local_path,
              )

if __name__ == "__main__":
    main()
