# -*- coding: utf-8 -*-
import csv
import pprint
from pyash import Move

mapping = {
    'n\xb0_de_transaction': 'id_transaction',
}


def clean(v):
    v = v.lower().strip()
    for s, d in (("'", ''), (' ', '_')):
        v = v.replace(s, d)
    return mapping.get(v, v)


def import_csv(filename):
    headers = []
    with open(filename, 'r') as fd:
        for line in csv.reader(fd):
            if not headers:
                headers = [clean(s) for s in line[:]]
                continue
            line = [l.decode('latin1') for l in line]
            line = dict(zip(headers, line))
            d = line['date'].split('/')
            line['date'] = '/'.join(reversed(d))
            line['amount'] = line['net']
            line['kind'] = 'Transfer'
            if line['avant_commission'] == '20,00':
                line['category'] = 'Cotisation'
                line['status'] = 'X'
            else:
                line['category'] = 'Other'
                line['status'] = 'P'
            line['description'] = line['nom']
            comment = (u'%(titre_de_lobjet)s\n'
                       u'    Commission: %(avant_commission)s%(commission)s\n'
                       u'    Transaction: %(id_transaction)s\n'
                       ) % line
            line['comment'] = comment.strip()
            print(Move.template.render(m=line).encode('utf8'))
