#!/usr/bin/env python

import argparse
import glob
import csv
import json
import datetime
import sys
import re
import os

class FileArgumentParser(argparse.ArgumentParser):
    """ Stolen from https://codereview.stackexchange.com/a/28614/102810 """
    def __is_valid_file(self, parser, arg):
        if not os.path.isfile(arg):
            parser.error('The file {} does not exist!'.format(arg))
        else:
            # File exists so return the filename
            return arg

    def __is_valid_directory(self, parser, arg):
        if not os.path.isdir(arg):
            parser.error('The directory {} does not exist!'.format(arg))
        else:
            # File exists so return the directory
            return arg

    def add_argument_with_check(self, *args, **kwargs):
        # Look for your FILE or DIR settings
        if 'metavar' in kwargs and 'type' not in kwargs:
            if kwargs['metavar'] == 'FILE':
                type=lambda x: self.__is_valid_file(self, x)
                kwargs['type'] = type
            elif kwargs['metavar'] == 'DIR':
                type=lambda x: self.__is_valid_directory(self, x)
                kwargs['type'] = type
        self.add_argument(*args, **kwargs)

def process_weight_data(archive_path):
    records = []
    files=glob.glob(os.path.join(archive_path, 'MatthewRussell', 'Personal & Account', 'weight*'))
    print("found ", files)
    for fname in files:
        with open(fname) as f:
            data = json.load(f)
            for i in data:
                records.append(i)

    return records

def export_weight_data(records):
    with open('output.csv', mode='w') as f:
        writer = csv.writer(f)
        for r in records:
            datetime_obj = datetime.datetime.strptime(f'{r["date"]} {r["time"]}', '%m/%d/%y %H:%M:%S')
            writer.writerow([
                r['logId'],           # Log ID
                datetime_obj.date(),  # Date (dest sheet has messy format dates here)
                datetime_obj.year,  # Year
                datetime_obj.month, # Month
                datetime_obj.day,   # Day
                datetime_obj,         # Date (well formatted)
                r['weight'],
                '',                   # 3 day avg
                '',                   # 5 day avg
                '',                   # 7 day avg
                r['bmi'],
                r['fat'] if 'fat' in r else '',
                r['source']
            ])

def main():

    argument_parser = FileArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Import fitbit stats',
    )

    argument_parser.add_argument_with_check(
        '--archive', '-a',
        dest='archive_path',
        help='Uncompressed archive directory',
        metavar='DIR',
    )

    try:
        args = argument_parser.parse_args()
    except AttributeError as e:
        print(e, file=sys.stderr)
        exit(1)

    records = process_weight_data(args.archive_path)

    export_weight_data(records)

if __name__ == "__main__":
    main()
