# Github repository analyzer

## Requirements

This program requires Python 3.6 or higher.
First thing to do is to make a credentials file `auth.txt`.
There is an example of that file in `auth.txt.example`.

## Usage

This program may be run with one of the followwing commands:
```bash
python analyze.py --help  # Show help message
./analyze.py eIGato/github-repo-analyzer  # Analyze given repo
./analyze.py https://github.com/eIGato/github-repo-analyzer --branch dev  # Analyze given repo, branch 'dev'
./analyze.py github.com/eIGato/github-repo-analyzer --branch=dev  # Same as previous
./analyze.py --since 2018-08-08 --until '2018-08-09T12:00:00Z' eIGato/github-repo-analyzer  # Analyze only 36 hours
```
