#!/usr/bin/env python3

import os
import os.path
import re
import sys

import xmltodict

months = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12',
}

for k, v in list(months.items()):
    months[k[:3]] = v

def main(argv):
    for path in argv:
        dname, fname = os.path.split(path)

        with open(path, 'rb') as f:
            doc = xmltodict.parse(f)

        date = doc['gpx']['metadata'].get('time')
        if date:
            date = date.split('T')[0]
        else:
            # missing <time> in metadata, assume same as other connector
            assert 'UTBDR-to-IDBDR' in fname, fname
            date = '2019-04-15'

        s = fname
        if mobj := re.match('^(.*)Connector[-]{0,1}(20[123][0-9]-[0-9]{2}-[0-9]{2}){0,1}(?:-Dirt){0,1}\.gpx$', fname):
            s, dt = mobj.groups()
            L = [_ for _ in s.replace('_', '-').split('-') if _]
            assert L[1] == 'to'

            for i in (0, 2):
                if len(L[i]) == 2:
                    L[i] += 'BDR'

            if dt and dt > date:
                date = dt

            s = '-'.join(L) + f'-Connector-{date}.gpx'
        elif mobj := re.match('^BDR-X-Red-Desert-Wyoming-(20[123][0-9])-([0-9]{2})-([0-9]{2}).gpx$', fname):
            year, month, day = mobj.groups()
            dt = f'{year}-{month}-{day}'
            if dt > date:
                date = dt
            s = f'WYBDRX-Red-Desert-{date}.gpx'
        elif mobj := re.match('^BlackHills-BDRX-(' + '|'.join(months) + ')(20[123][0-9]).*\.gpx$', fname):
            month, year = mobj.groups()
            month = months[month]
            dt = f'{year}-{month}-01'
            if dt > date:
                date = dt
            s = f'SDBDRX-Black-Hills-{date}.gpx'
        elif mobj := re.match('^SteensAlvord-BDRX-(' + '|'.join(months) + ')(20[123][0-9]).*\.gpx$', fname):
            month, year = mobj.groups()
            month = months[month]
            dt = f'{year}-{month}-01'
            if dt > date:
                date = dt
            s = f'ORBDRX-Steens-Alvord-{date}.gpx'
        elif mobj := re.match('^PA-Wilds-BDRX-(' + '|'.join(months) + ')(20[123][0-9]).*\.gpx$', fname):
            month, year = mobj.groups()
            month = months[month]
            dt = f'{year}-{month}-01'
            if dt > date:
                date = dt
            s = f'PABDRX-Wilds-{date}.gpx'
        elif mobj := re.match('^CABDR-([NS])-(' + '|'.join(months) + ')(20[123][0-9]).*\.gpx$', fname):
            ns, month, year = mobj.groups()
            month = months[month]
            dt = f'{year}-{month}-01'
            if dt > date:
                date = dt
            s = f'CABDR-{ns}-{date}.gpx'
        elif mobj := re.match('^([A-Z]{2}BDR)-(' + '|'.join(months) + ')(20[123][0-9]).*\.gpx$', fname):
            s, month, year = mobj.groups()
            month = months[month]
            dt = f'{year}-{month}-01'
            if dt > date:
                date = dt
            s = f'{s}-{date}.gpx'

        if s != fname:
            print(f'Rename {fname} to {s}')
            os.rename(path, os.path.join(dname, s))

if __name__ == '__main__':
    main(sys.argv[1:])
