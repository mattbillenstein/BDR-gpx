import json
import os
import os.path
import re
import sys

import requests
import xmltodict

# six digits good to ~0.11m - 4.33in, five good to about 1.1m,
# four good to about 11m
latlondigits = 5
latlonfmt = '%.' + str(latlondigits) + 'f'
latlonptfmt = latlonfmt + ',' + latlonfmt

colors = {
    'even': 'Blue',    # 1 is the 0'th track...
    'odd': 'DarkBlue',
    'hard': 'Red',
    'alt': 'Green',
    'bypass': 'Yellow',
}

hexcolor = {
    'Blue': '3F46F5',
    'DarkBlue': '00045C',
    'Red': 'E93223',
    'Green': '00C000',
    'DarkGreen': '007000',
    'Magenta': 'FF00FF',
    'Yellow': 'FFEF00',
    'Cyan': '00FFFF',
    'Black': '000000',
}

mei = getattr(sys, '_MEIPASS', '.')

with open(os.path.join(mei, 'elevation-api.key')) as f:
    GOOGLE_MAPS_KEY = f.read().strip()

try:
    with open('output/elevation-cache.json') as f:
        _elevation_cache = json.loads(f.read())
except FileNotFoundError:
    _elevation_cache = {}

def canon_point(pt):
    return (round(float(pt[0]), latlondigits), round(float(pt[1]), latlondigits))

def get_elevations(points):
    url = 'https://maps.googleapis.com/maps/api/elevation/json'

    L = []
    for pt in points:
        key = latlonptfmt % canon_point(pt)
        if key not in _elevation_cache:
            L.append(key)

    bulk = 100
    for i in range(0, len(L), bulk):
        params = {
            'locations': '|'.join(L[i:i+bulk]),
            'key': GOOGLE_MAPS_KEY,
        }

        r = requests.get(url, params=params)
        assert r.ok, (r.content, params['locations'], len(params['locations']))

        data = r.json()
        for result in data['results']:
            key = latlonptfmt % canon_point((result['location']['lat'], result['location']['lng']))
            _elevation_cache[key] = '%.2f' % (result['elevation'])

    return {canon_point(pt): _elevation_cache[latlonptfmt % canon_point(pt)] for pt in points}

def getlist(elem, key):
    L = elem.get(key, [])
    if not isinstance(L, list):
        L = [L]
    return L

def process(fin, fout, log=print, preserve_colors=False):
    with open(fin, 'rb') as f:
        doc = xmltodict.parse(f)

    gpx = doc['gpx']

    for wpt in getlist(gpx, 'wpt'):
        for k in ('@lat', '@lon'):
            wpt[k] = latlonfmt % (float(wpt[k]))

        # replace long runs of newlines - NE/MABDR has thousands of
        # these...
        for k in ('name', 'cmt', 'desc'):
            if wpt.get(k):
                s = wpt[k]
                while '\n\n' in s:
                    s = s.replace('\n\n', '\n')
                wpt[k] = s

    i = 0
    for trk in getlist(gpx, 'trk'):
        # FIXME - gpxx extensions and so forth?

        # fixup name
#            s = trk['name']
#            if s.split()[0].lower() in ('alt', 'ext'):
#                # make section come first, then alt/ext
#                L = s.split()
#                L[0], L[1] = L[1], L[0]
#                s = ' '.join(L)
#                trk['name'] = s

        if preserve_colors:
            color = trk['extensions']['gpxx:TrackExtension']['gpxx:DisplayColor']
        else:
            # assign color - alternating blue/darkblue for regular route, green
            # easy, red hard, magenta alternate
            s = ' ' + trk['name'].lower() + ' '
            if 'BlackHills' in fin and 'BDRX3 - Hill City' in trk['name']:
                # not same as 1
                color = 'Magenta'
            elif ' temp bypass ' in s:
                color = colors['bypass']
            elif ' harder ' in s:
                color = colors['hard']
            elif ' expert ' in s:
                color = colors['hard']
            elif ' alt ' in s:
                color = colors['alt']
            elif ' ext ' in s:
                color = colors['alt']
            else:
                if i % 2 == 0:
                    color = colors['even']
                else:
                    color = colors['odd']
                i += 1

        log(f'{color:10s} -- {trk["name"]}')

        # Garmin
        trk['extensions']['gpxx:TrackExtension']['gpxx:DisplayColor'] = color

        # Gaia
        trk['extensions']['line'] = {
            '@xmlns': 'http://www.topografix.com/GPX/gpx_style/0/2',
            'color': hexcolor[color],
        }

        for trkseg in getlist(trk, 'trkseg'):
            trkpts = []
            last = None
            for trkpt in getlist(trkseg, 'trkpt'):
                for k in ('@lat', '@lon'):
                    trkpt[k] = latlonfmt % (round(float(trkpt[k]), latlondigits))

                # remove time, it's not consistently present...
                for k in ('time',):
                    if k in trkpt:
                        trkpt.pop(k, None)

                # filter out duplicate points
                pt = (trkpt['@lat'], trkpt['@lon'])
                if pt != last:
                    trkpts.append(trkpt)
                last = pt

            if trkpts:
                trkseg['trkpt'] = trkpts

                # FIXME, just filling in missing elevations atm, seems to
                # line up pretty well with existing elevation data, but
                # perhaps we should just replace all the elevations with
                # google data?
                missing = []
                for trkpt in trkpts:
                    ele = trkpt.get('ele') or '0'
                    if int(float(ele)) == 0:
                        missing.append((trkpt['@lat'], trkpt['@lon']))
                    else:
                        trkpt['ele'] = str(round(float(ele), 2))

                elevations = get_elevations(missing)
                for trkpt in trkpts:
                    pt = canon_point((trkpt['@lat'], trkpt['@lon']))
                    if pt in elevations:
                        trkpt['ele'] = elevations[pt]

    with open(fout, 'w') as f:
        f.write(xmltodict.unparse(doc, pretty=True, indent='  '))

    with open('output/elevation-cache.json', 'w') as f:
        f.write(json.dumps(_elevation_cache, indent=2))
