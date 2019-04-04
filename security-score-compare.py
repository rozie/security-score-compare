#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import re
import sqlite3

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import requests

import yaml

logger = logging.getLogger(__name__)


def get_data_from_db(dbfile, days, platform):
    con = None
    data = {}
    day_query = "-{} days".format(days)
    #print(dbfile, days, platform)
    try:
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        query = """SELECT  DISTINCT substr(timestamp, 1, 10), nick, score
                FROM score WHERE platform=?
                AND timestamp > datetime('now', ?)
                ORDER BY timestamp;"""
        cur.execute(query, (platform, day_query))
        rows = cur.fetchall()
        dates_tmp = set()
        nicks_tmp = {}
        for row in rows:
            (date, nick, score) = row
            dates_tmp.add(date)
            if not nicks_tmp.get(nick):
                nicks_tmp[nick] = []
                nicks_tmp[nick].append(score)
            else:
                nicks_tmp[nick].append(score)
        data['dates'] = list(dates_tmp)
        data['scores'] = nicks_tmp
        # pad missing with zeros
        for nick in data.get('scores'):
            days_of_data = int(len(data['scores'][nick]))
            dates_count = int(len(data['dates']))
            print(nick, days_of_data, dates_count)
            if days_of_data < dates_count:
                data['scores'][nick] = ([0] * (dates_count - days_of_data)) + data['scores'][nick]
    except Exception as e:
        logging.error("DB oparation failed %s", e)
    finally:
        if con:
            con.close()
    return data



def store_to_db(dbfile, platform, nick, score):
    con = None
    try:
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        query = """INSERT INTO score (platform, nick, score) VALUES (?, ?, ?)"""
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

    dbfile = data.get('sqlite', {}).get('db', 'score.db')

    # draw a chart
    if args.plot:
        data = get_data_from_db(dbfile, args.time, args.platform)
        x_axis = data.get('dates')
        print(x_axis)
        fig = plt.figure()
        ax = plt.subplot(111)
        for nick in data.get('scores'):
            values = data['scores'][nick]
            print(nick, values)
            ax.plot(x_axis, values, label=nick)
        plt.legend(loc=3)
        fig.savefig(args.output)

    # grab data from all platforms
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
        default=False, action='store_true',
        help="Plot a chart")
    parser.add_argument(
        '-t', '--time', required=False, type=int,
        default=7,
        help="How many days")
    parser.add_argument(
        '-o', '--output', required=False,
        default='output.png',
        help="Output chart file")
    parser.add_argument(
        '-P', '--platform', required=False,
        default='rootme',
        help="Platform to make chart for"
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
