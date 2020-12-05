# nexrad-aws
Simple script to automate batch downloading of nexrad data from Amazon Web Services.

## Basic Setup Notes
This script requires Python 3.xx and the s3fs module. The easiest way to set this up is to [download Anaconda](https://www.anaconda.com/products/individual) and then run:

```
conda env create -f environment.yml
```

This will create an Anaconda environment with the necessary libraries.

## Useage
If you are using Anaconda, simply type `conda activate nexrad-aws` to activate the environment that was installed in the setup section above.

The `get_nexrad.py` script takes a few command-line arguments:

```
python get_nexrad.py -s START_TIME -e END_TIME -r RADAR_ID [ -p LOCAL_PATH]
```
**The following arguments are required:**
* `START_TIME`  Desired first scan time in the form YYYY-MM-DD/HHmm
* `END_TIME` Desired last scan time in the form YYYY-MM-DD/HHmm
* `RADAR_ID` 4-letter radar id to download. Can be upper or lower case.

**The following argument is optional:**
* `LOCAL_PATH` Full path to download files to on the local filesystem. If none specified, files will be downloaded to the current working directory.

If your request is successful, you'll see a prompt like:

```
==> Number of requested files: __
==> Requested download is approximately:  __ MB
==> Files will be downloaded to: __ Continue? [y|n]
```

Type `y` to continue with the download or `n` to abort. 
