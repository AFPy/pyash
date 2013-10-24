#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jinja2 import Template
from chut import console_script
from decimal import Decimal
import datetime

DATE_FORMAT = '%Y/%m/%d'

table = Template('''
{%- for label, amount in values %}
{{ '+-{0:20s}+{1:11s}-+'.format('-' * 20, '-' * 11) }}
{{ '| {0:20s}|{1:11.2f} |'.format(label, amount) }}
{%- endfor %}
{{ '+-{0:20s}+{1:11s}-+'.format('-' * 20, '-' * 11) }}
''')


def render_table(values):
    return table.render(values=values) + '\n'


class Balance(dict):

    def __init__(self, reverse=False):
        self.reverse = reverse
        self.coef = reverse and 1 or -1
        self.title = reverse and u'Recettes' or u'Depenses'

    def __iter__(self):
        items = sorted([(v * self.coef, k) for k, v in self.items()],
                       reverse=True)
        return iter([(k, v) for v, k in items])

    def sum(self):
        return sum(self.values()) * self.coef

    def __str__(self):
        title = u'%s\n%s\n' % (self.title, u'=' * len(self.title))
        values = list(self) + [('Total', self.sum())]
        return title + render_table(values)


class Move(dict):

    template = Template(u'''
{{ m.date }} {{ m.amount }}€ {{m.kind}} {{ m.category }} {{ m.status }}
    {{ m.description }}
    {{ m.comment or '' }}
''')

    def __init__(self, line):
        date_str, amount_str, kind, category, status = line.strip().split(' ')
        date = datetime.datetime.strptime(date_str, DATE_FORMAT)
        amount = Decimal(amount_str.rstrip(u'\u20ac'))
        self.update({
            'date': date,
            'amount': amount,
            'category': category,
            'status': status,
            'kind': kind,
            'description': None,
            'comment': '',
        })

    def add(self, line):
        if line.strip():
            if self['description'] is None:
                self['description'] = line.strip()
            else:
                self['comment'] += line.strip(' ')

    def __cmp__(self, other):
        return cmp(self['date'], other['date'])

    def __str__(self):
        m = dict(self.copy())
        m['date'] = self['date'].strftime(DATE_FORMAT)
        return self.template.render(m=m).encode('utf8').lstrip()


class MovesFile:

    def __init__(self, args):
        self.args = args
        self.file = open(args['-i'], 'r')
        self.start_date = datetime.datetime.strptime(args['-s'], DATE_FORMAT)
        if args['-e'] == 'Now':
            self.end_date = datetime.datetime.now()
        else:
            self.end_date = datetime.datetime.strptime(args['-e'], DATE_FORMAT)
        self.moves = sorted(self.parse())
        self.balances = {
            'in': Balance(reverse=True),
            'out': Balance(),
        }
        for move in self.moves:
            if move['amount'] > 0:
                balance = self.balances['in']
            else:
                balance = self.balances['out']

            category = move['category']
            if category in balance:
                balance[category] += move['amount']
            else:
                balance[category] = move['amount']

    def title(self):
        title = 'Période du %s au %s\n' % (
            self.start_date.strftime(DATE_FORMAT),
            self.end_date.strftime(DATE_FORMAT)
        )
        sep = '=' * len(title)
        sep += '\n'
        return sep + title + sep

    def balance(self):
        i = self.balances['in']
        o = self.balances['out']
        values = [
            (i.title, i.sum()),
            (o.title, o.sum()),
            ('Resultat', i.sum() - o.sum()),
        ]
        return render_table(values=values)

    def iterator(self):
        with open(self.args['-i']) as fd:
            for line in fd:
                yield line.decode('utf8')

    def parse(self):
        move = None
        line = True
        fd = self.iterator()
        line = fd.next()
        while True:
            if line[:4].isdigit():
                move = Move(line)
                line = fd.next()
                while not line[:4].isdigit():
                    move.add(line)
                    try:
                        line = fd.next()
                    except StopIteration:
                        break
                if self.filter(move):
                    yield move
            else:
                line = fd.next()

    def filter(self, move):
        if self.args['-g'] and self.args['-g'] not in str(move).lower():
            return
        if self.args['-p'] and not move['status'].upper() == 'P':
            return
        if self.args['-x'] and not move['status'].upper() == 'X':
            return
        if self.start_date <= move['date'] <= self.end_date:
            return True


@console_script
def pyash(args):
    """
    Usage: %prog [options] balance
           %prog [options] show

    -i FILENAME     Input file [Default: afpy.ash]
    -s DATE         Start date [Default: 2000/01/01]
    -e DATE         Start date [Default: Now]
    -p              Show pendings
    -x              Show checked
    -g PATTERN      Grep
    """
    moves = MovesFile(args)
    if args['balance']:
        print(moves.title())
        print(moves.balance())
        print(moves.balances['in'])
        print(moves.balances['out'])
    elif args['show']:
        for m in moves.moves:
            print(m)

if __name__ == '__main__':
    pyash()
