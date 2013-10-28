# -*- coding: utf-8 -*-
import csv
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
    lines = []
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
            line['commission'] = line['commission'].strip('-')
            comment = (u'%(titre_de_lobjet)s\n'
                       u'    Commission: %(avant_commission)s-%(commission)s\n'
                       u'    Transaction Paypal: %(id_transaction)s\n'
                       ) % line
            line['comment'] = comment.strip()
            lines.append(((int(d) for i in d), line))
    for d, line in reversed(lines):
        print(Move.template.render(m=line).encode('utf8'))
