#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import re
import sqlite3

import requests
import yaml

logger = logging.getLogger(__name__)


def store_to_db(dbfile, platform, nick, score):
    con = None
    try:
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        query = """INSERT INTO score (platform, nick, score VALUES (?, ?, ?)"""
        cur.execute(query, (platform, nick, score))
        conn.commit()
    except Exception as e:
        logging.error("DB oparation failed %s", e)
    finally:
        if con:
            con.close()


def get_data(url):
    try:
        r = requests.get(url, timeout=15)
    except (requests.HTTPError, requests.ConnectionError) as e:
        raise RuntimeError(str(e))
    except (ValueError, TypeError) as e:
        raise RuntimeError(str(e))
    return r.text


def get_score(regexp, text):
    score = 0
    for line in text:
        m = re.search(regexp, line)
        if m:
            score = m.group(1)
            break
    return score


def main():
    args = parse_arguments()

    # set verbosity
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # load config file
    try:
        with open(args.config, "r") as config:
            data = yaml.safe_load(config)
    except Exception as e:
        logger.error("Couldn't read config file %s", e)

    # rootme
    dbfile = data.get('sqlite', {}).get('db', 'score.db')

    if args.plot:
        pass
    else:
        tmpplatforms = data['platforms']
        for platform in tmpplatforms:
            regexp = tmpplatforms[platform]['regexp']
            logging.debug("%s regexp %s", platform, regexp)
            tmpnicks = tmpplatforms[platform]['nicks']
            for nick in tmpnicks:
                score = None
                url = tmpnicks[nick]
                logging.debug("Nick: %s URL: %s", nick, url)
                data = get_data(url).splitlines()
                score = get_score(regexp, data)
                logging.info("The score for nick %s on platform %s is %s",
                             nick, platform, score)
                if not args.dryrun:
                    if score:
                        store_to_db(dbfile=dbfile, platform=platform,
                                    nick=nick, score=score)
                    else:
                        logging.error("Can't get score for %s, %s", nick, url)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Security Score Compare')
    parser.add_argument(
        '-d', '--dryrun', required=False,
        default=False, action='store_true',
        help="Just print data, don't change anything")
    parser.add_argument(
        '-v', '--verbose', required=False,
        default=False, action='store_true',
        help="Provide verbose output")
    parser.add_argument(
        '-c', '--config', required=False,
        default="example.yaml",
        help="Configuration file")
    parser.add_argument(
        '-p', '--plot', required=False,
        default=False,
        help="Plot a chart")
    parser.add_argument(
        '-t', '--time', required=False,
        default=28,
        help="How many days")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
