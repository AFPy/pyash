import csv
from datetime import datetime

from chut import console_script
from jinja2 import Template


TEMPLATE = '''
{{ r.date }} {{ r.amount }}€ {{r.kind}} {{ r.type }}{{ r.status }}
    {{ r.description }}
    {{ r.comment or '' }}

'''

types = {
    'Teeshirt': 'Goodies',
    'FraisPubli': 'Goodies',
    'Alimentation': 'Alimentation',
    'Transport': 'Transport',
    'Partenaire:PyConFR08': 'Pycon08',
    'Partenaire:PyConFR07': 'PyCon07',
    'SCBC': 'VariousEvents',
    'Fraisbanca': 'FraisBanque',
    'Hébergement': 'Hosting',
    'Fraish': 'Hebergement',
    'Fraisdeser': 'FraisDivers',
    'VariousEvents': 'SponsoringEvents',
    'SponsoringEvenements': 'SponsoringEvents',
}


def transform_item(record):
    record = {key.lower(): value for key, value in record.items()}
    record['date'] = datetime.strptime(record['date'],
                                       '%d/%m/%y').strftime('%Y/%m/%d')
    record['amount'] = float(record['amount'].replace(',', '.'))
    record['comment'] = record['comment'].decode('utf8') or None
    record['description'] = record['description'].decode('utf8') or None
    record['type'] = record['type'].decode('utf8').replace(' ', '')
    record['info'] = record['info'].decode('utf8') or None

    if record['info'] is not None:
        if record['comment'] is None:
            record['comment'] = record['info']
        else:
            record['comment'] += ' ; ' + record['info']

    if record['amount'] == 0:
        record['type'] = 'Cotisation'
        record['amount'] = 20.

    st = record['status']
    if st.startswith('Pending'):
        record['status'] = ' P'
    else:
        record['status'] = ' X'

    t = record['type']
    for k, v in types.items():
        if t.startswith(k):
            t = v
    record['type'] = t
    if not t:
        if record['description'] == 'Sac Ecobags':
            t = 'Goodies'
        elif record['amount'] == 20:
            t = 'Cotisation'
        else:
            raise LookupError(t)
        record['type'] = t

    k = record['kind']
    if k.startswith('TransferTransaction'):
        k = 'Transfer'
    elif k.startswith('ServiceCharge'):
        k = 'ServiceCharge'
    elif k.startswith('StandingOrder'):
        k = 'Order'
    elif k.startswith('Check'):
        k = 'Check'
    elif k.startswith('CreditCard'):
        k = 'CreditCard'
    elif k.startswith('Cash'):
        k = 'Cash'
    elif k.startswith('Other'):
        if t == 'Don':
            k = 'Transfer'
        elif record['description'] == 'Sac Ecobags':
            record['type'] = 'Goodies'
            k = 'Check'
        elif 'shirt' in record['description']:
            t = 'Goodies'
            k = 'Check'
        else:
            k = 'Other'
            if record['amount'] != 20:
                if 'pycon' in record['description'].lower():
                    k = 'Check'
                elif record['amount'] in (100, 200, 400):
                    k = 'Check'
    else:
        raise LookupError(k)
    record['kind'] = k

    for key in ['conciled date', 'ending date', 'frequency', 'taxes']:
        record[key] = record[key].decode('utf8')
    return record


def print_record(record):
    template = Template(TEMPLATE)
    move = template.render(
        r=record,
    ).encode('utf8')
    print(move.strip() + '\n')


def parse_csv(filename):
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for record in reader:
            yield transform_item(record)


@console_script
def csv2pyash(args):
    """Usage: %prog <csv>"""
    records = parse_csv(args['<csv>'])
    for record in records:
        print_record(record)


if __name__ == '__main__':
    csv2pyash()
