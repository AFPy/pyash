#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jinja2 import Template
from chut import console_script
from decimal import Decimal
from pprint import pprint
import datetime

DATE_FMT = '%Y/%m/%d'

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

    def __init__(self, m, i, line):
        self.index = m
        self.line_number = i
        date_str, amount_str, kind, category, status = line.strip().split(' ')
        date = datetime.datetime.strptime(date_str, DATE_FMT)
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

    def __getattr__(self, attr):
        return self[attr]

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
        m['date'] = self['date'].strftime(DATE_FMT)
        return self.template.render(m=m).encode('utf8').strip() + '\n\n'


class MovesFile:

    def __init__(self, args):
        self.args = args
        self.file = open(args['-i'], 'r')
        if '-s' in args:
            self.start_date = datetime.datetime.strptime(args['-s'], DATE_FMT)
        else:
            self.start_date = datetime.datetime(1900, 1, 1)

        if '-e' not in args:
            args['-e'] = 'Now'
        if args['-e'] == 'Now':
            self.end_date = datetime.datetime.now()
        else:
            self.end_date = datetime.datetime.strptime(args['-e'], DATE_FMT)

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
        start_date = self.moves[0]['date']
        end_date = self.moves[-1]['date']
        title = 'Période du %s au %s\n' % (
            start_date.strftime(DATE_FMT),
            end_date.strftime(DATE_FMT)
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
        if self.args.get('--period'):
            periode = '-- ' + self.args['--period']
        else:
            periode = None
        i = 0
        with open(self.args['-i']) as fd:
            for line in fd:
                i += 1
                line = line.decode('utf8')
                if periode and periode is not True:
                    if line.startswith(periode):
                        periode = True
                    continue
                if periode is True and line.startswith('!'):
                    raise StopIteration()
                if line[0] in '$!#-':
                    continue
                yield i, line

    def parse(self):
        move = None
        fd = self.iterator()
        i, line = fd.next()
        m = 0
        while True:
            if line[:4].isdigit():
                m += 1
                move = Move(m, i, line)
                i, line = fd.next()
                while not line[:4].isdigit():
                    move.add(line)
                    try:
                        i, line = fd.next()
                    except StopIteration:
                        break
                if self.filter(move):
                    yield move
            else:
                i, line = fd.next()

    def filter(self, move):
        g = self.args.get('-g', '')
        if g and g not in str(move).lower():
            return
        if self.args.get('-p') and not move['status'].upper() == 'P':
            return
        if self.args.get('-x') and not move['status'].upper() == 'X':
            return
        if self.start_date <= move['date'] <= self.end_date:
            return True


@console_script
def pyash(args):
    """
    Usage: %prog [options] balance
           %prog [options] show
           %prog validate
           %prog json
           %prog [options] paypal <csv>

    -i FILENAME     Input file [Default: afpy_gestion/compta/afpy.ash]
    -s DATE         Start date [Default: 2000/01/01]
    -e DATE         End date [Default: Now]
    -p              Pendings
    -x              Checked
    -g PATTERN      Grep
    --period PERIOD Only show period
    """
    if args['paypal']:
        from . import paypal
        paypal.import_csv(args['<csv>'])
    if args['validate']:
        out = ''
        moves = MovesFile({'-i': args['-i']})
        for m in moves.moves:
            out += str(m)
        return
    if args['json']:
        out = {}
        moves = MovesFile({'-i': args['-i']})
        for m in moves.moves:
            for k, v in m.items():
                if k not in ('amount', 'date', 'description', 'comment'):
                    s = out.setdefault(k, set())
                    s.add(v)
        for k, v in out.items():
            out[k] = sorted(v)
        pprint(out)
        return
    moves = MovesFile(args)
    if not moves.moves:
        return
    if args['balance']:
        print(moves.title())
        print(moves.balance())
        print(moves.balances['in'])
        print(moves.balances['out'])
    elif args['show']:
        for m in moves.moves:
            print('{0}\n    line: {1}\n'.format(str(m).strip(), m.line_number))

if __name__ == '__main__':
    pyash()
