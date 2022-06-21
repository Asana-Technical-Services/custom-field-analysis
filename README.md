# Field Analysis script

This python script is used to generate a CSV of fields in an asana instance and a count of how frequently they are used

## Requirements

This script is written using Python 3.8, though it should be compatible with most 3.x versions of python.

check your version of python locally installed with the command:

```
python -V
```

If you need to install a newer version of python, you can do so at https://www.python.org/downloads/

_Be sure to install certificates (by running the appropriate script in the python folder) if you download a new version of python_

## Installing the script

This python script has been packaged into an installable package, which can be found under the `/dist` folder. both a tar.gz and .whl file can be found. It's recommended to use the .whl file as it is generally more consistent.

To install, run the python installer `pip` with the path to the whl file. you can usually drag and drop a file into the command line terminal to get the path

```
pip install /path/to/dist/fieldanalysis.whl
```

Once installed, the script can be run via

```
fieldanalysis
```

On installation, you may recieve a warning like:

```
WARNING: The script fieldanalysis is installed in '/Library/Frameworks/python.framework/Versions/3.9/bin' which is not on PATH
```

To add that directory to path, simply run the following command with your path from above filled in:

```
export PATH=$PATH:your/path/here
```

e.g. `export PATH=$PATH:/Library/Frameworks/python.framework/Versions/3.9/bin`

This should allow you to run this script from the single `fieldanalysis` command

Alternatively, a 'runfieldanalysis.py' file has been provided in the base directory to run the script directly via

```
python path/to/runfieldanalysis.py
```

## Operation

Run the script using

```
fieldanalysis
```

or alternatively:

```
python fieldanalysis.py
```

The script interactively asks for 4 arguments:

- a personal access token (PAT)
- your workspace gid

Personal access tokens are how the script authenticates with asana to create these projects as your Asana user. To get one, follow this Asana guide article https://asana.com/guide/help/api/api

You will be given an option of possible workspaces to analyize. be mindful that large domains can take a long time!

the standard fields outputted are the gid, name, and type for the custom field, as well as the 'count' of number of projects the field is used in. Be mindful that this does not include portfolios.

To get more information on a custom field, you can request the custom field record by using its gid with the Asana API, as documented here: https://developers.asana.com/docs/get-a-custom-field

## Rate Limits

Due to the high volume of API calls this script makes, it may sometimes hit rate limits and need to set some delay between its API calls. The exact amount of delay will be printed to the console. Because the script will be running many calls in parallel, this message may print multiple times, once for each API call that was blocked due to rate limiting. These wait times will not be additive, since the calls are running in parallel. Once the wait duration is up, each API call will be retried with increasing delay until it succeeds. After ~10 tries (which would take almost 3 minutes of attempts) the individual api call will be canceled.

## Code Structure

The package is written as a basic interactive script, coordinated by the main function in projectupload.py

The codebase is laid out as follows:

```
├── README.md
├── dist/
├── fieldanalysis
│   ├── asanaUtils
│   │   └── client.py
│   ├── menu.py
│   └── fieldanalysis.py
├── fieldanalysis.egg-info/
├── pyproject.toml
├── requirements.txt
├── runfieldanalysis.py
├── setup.cfg
└── setup.py
```

All source code is contained within the `fieldanalysis` directory. The fieldanalysis function within the fieldanalysis.py file coordinates all other functionality of the script.

The menu.py file contains the menu and a few helper functions to gather user input and map the CSV to the portfolio fields.

The asanaUtils directory contains a client.py file, which handles formatting and sending API calls, along with handling rate limits.

The `dist` and `fieldanalysis.egg-info` directories contain build information generated when packaging the project.

## Testing and Re-building a new version of the package

To test and run the script code directly, you can run a file in the top of this directory which imports the package and runs it.

```
python runfieldanalysis.py
```

To re-build the packages in the `dist` folder (after making changes to the script, for example), you'll need the `setuptools` package (installed via `pip install setuptools`). Then while in this directory, run:

```
python -m build
```

Changes to the configuration, name, or version, should primarily be made through the setup.cfg file.
