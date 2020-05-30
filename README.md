# github-stats
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python scripts to gather github statistics.

## Requirements

In order to run the scripts, we need to install dependecies and list the usernames we'll be analysing.

### Installing dependencies

Run the following command on your terminal:

```sh
pip install -r requirements.txt
```

### Github API Token

In order authenticate the API requests, we must first [generate a Github personal token](https://github.com/settings/tokens),
containing the `read:user` scope.

Then we just set the `GITHUB_TOKEN` environment variable:

```sh
GITHUB_TOKEN=<token>
```

or in fish:

```sh
set -x GITHUB_TOKEN "<token>"
```

### Github username list

There are two different ways to determine what users we will be scraping:

#### Using `usernames.txt` file

`usernames.txt` is a text file listing github usernames we are interested in gathering statistics from.

It should have one username per line, for example:

```
fredericojordan
gvanrossum
```

#### Using `GITHUB_USERNAMES` environment variable

If a `usernames.txt` file is not found, the second option is using a `GITHUB_USERNAMES` env var.

The usernames are separated by a comma, for example (in bash):

```sh
GITHUB_USERNAMES="fredericojordan,gvanrossum"
```

or in fish:

```sh
set -x GITHUB_USERNAMES "fredericojordan,gvanrossum"
```

## Running the script

Simply run the `stats.py` script from your terminal:

```sh
python stats.py
```

Output:

```sh
1. (2855) fredericojordan
2. (1040) gvanrossum
```

## (Optional) Start web server

We may also use `gunicorn` to serve a simple static web page displaying the statistics:

```sh
gunicorn server:app
```

and then navigate to [localhost:8000](http://localhost:8000) on a browser of your choice.
