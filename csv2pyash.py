#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from datetime import datetime

from jinja2 import Template


TEMPLATE = u'''{{ date.strftime('%Y/%m/%d') }} {{ amount }}€ {{ type }}
    {{ description }}

'''


def transform_item(record):
    record = {key.lower(): value for key, value in record.items()}
    record['date'] = datetime.strptime(record['date'], '%d/%m/%y').date()
    record['amount'] = float(record['amount'].replace(',', '.'))
    record['comment'] = record['comment'] or None
    record['description'] = record['description'] or None
    record['type'] = record['type'] or None
    record['info'] = record['info'] or None

    if record['info'] is not None:
        if record['comment'] is None:
            record['comment'] = record['info']
        else:
            record['comment'] += u' ; ' + record['info']

    for key in ['conciled date', 'ending date', 'frequency', 'status', 'kind',
                'taxes', 'info']:
        del record[key]
    return record


def print_record(record):
    template = Template(TEMPLATE)
    move = template.render(
        date=record['date'],
        description=record['description'],
        type=record['type'].replace(' : ', ':'),
        amount=record['amount']
    )
    print(move)


def parse_csv(filename):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for record in reader:
            yield transform_item(record)


if __name__ == '__main__':
    import sys
    records = parse_csv(sys.argv[1])
    for record in records:
        print_record(record)
