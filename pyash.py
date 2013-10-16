#!/usr/bin/env python

import datetime

from decimal import Decimal


class MovesFile:

    def __init__(self, filename):
        assert filename, 'A filename must be given'
        self.file = open(filename, 'r')

    def parse(self):
        move = None
        for line in self.file:
            if move and (line in ['', '\n'] or line[:4] != '    '):
                yield move
                move = None
            if line == '':
                break
            if line == '\n':
                continue
            if move and line[:4] == '    ':
                    move['description'] += line[4:]
            if not move:
                move = self.parse_1st_line(line)
        self.file.close()

    def parse_1st_line(self, line):
        date_str, amount_str, category = line[:-1].split(' ', 2)
        date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
        amount = Decimal(amount_str[:-1])
        return {
            'date': date,
            'amount': amount,
            'category': category,
            'description': '',
        }

    def balance(self):
        balance_in = {}
        balance_out = {}
        for move in self.parse():
            if move['amount'] > 0:
                balance = balance_in
            else:
                balance = balance_out

            category = move['category']
            if category in balance:
                balance[category] += move['amount']
            else:
                balance[category] = move['amount']
        return balance_in, balance_out


TEMPLATE = u'''Revenus :
{%- for category, amount in balance_in.items() %}
     {{ category }} : {{ amount }}
{%- endfor %}
     =============================
     Total : {{ balance_in.values()|sum }}

Dépenses :
{%- for category, amount in balance_out.items() %}
     {{ category }} : {{ amount }}
{%- endfor %}
     =============================
     Total : {{ balance_out.values()|sum }}

'''


def print_balance(balance_in, balance_out):
    from jinja2 import Template
    template = Template(TEMPLATE)
    print(template.render(balance_in=balance_in, balance_out=balance_out))

if __name__ == '__main__':
    import sys
    moves = MovesFile(sys.argv[1])
    balin, balout = moves.balance()
    print_balance(balin, balout)
