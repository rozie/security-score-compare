# security-score-compare
Tool to compare score on security learning platforms such as http://root-me.org/,
https://ringzer0ctf.com/, https://www.hackthebox.eu/ and https://ctflearn.com/
between different users.

Description
---------
Security Score Compare is simple tool to watch and compare progress on security
learning platforms. Dedicated to small groups of friends or colleagues from the
same company.
Consist of two parts or modes. One for gathering scores, one for plotting graphs.

Intended to run from cron, stores data to SQLite database. Easily configurable
by editing YAML file.

Supported platforms
---------
- http://root-me.org/
- https://ringzer0ctf.com/
- https://www.hackthebox.eu/
- https://ctflearn.com/

Requirements
---------
- Python 3.5 (or newer)
- modules listed in requirements.txt

Configuration
---------
Configuration is performed by YAML configruation file, which can be specified
by *--config* parameter. Example configuration is provided in *example.yaml*.

It has two main blocks: *platforms* and *sqlite*

The first one contains data about security platforms - how to get the score and
which user data to fetch.

The second one contains SQLite file location.

Usage
---------
- clone this repository
- pip install -r requirements.txt
- adjust config file (see example.yaml)
- run the script with --dryrun (-d) option
- if everything goes well, add to crontab
- create database with following schema:

  CREATE TABLE score (
          timestamp default current_timestamp,
          platform text,
          nick text,
          score integer
  );


- To draw a chart for rootme platform and last 7 days:
   security-score-compare.py -p -t 7 -P rootme -o /var/www/7_days_rootme.png

Notices
---------
- For https://www.hackthebox.eu/ works only for public profiles and returns
Hall of Fame position instead of score.
- If you use root-me.org, use API instead of HTML. Scraping HTML is no longer
reliable, leaving it only as fallback.

Contribution
---------
Help is always welcome, so clone this repository, send pull requests or create
issues if you find any bugs.

License
---------
See LICENSE file
