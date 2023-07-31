#!/usr/bin/env python3

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

with open('elevation-api.key') as f:
    GOOGLE_MAPS_KEY = f.read().strip()

try:
    with open('elevation-cache.json') as f:
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

def main(args):
    if not os.path.isdir('dist'):
        os.makedirs('dist')

    for fname in args:
        basename = os.path.split(fname)[1]

        with open(fname, 'rb') as f:
            doc = xmltodict.parse(f)

        gpx = doc['gpx']

        for wpt in getlist(gpx, 'wpt'):
            for k in ('@lat', '@lon'):
                wpt[k] = latlonfmt % (float(wpt[k]))

            # replace long runs of newlines - NE/MABDR has thousands of these...
            for k in ('name', 'cmt', 'desc'):
                if wpt.get(k):
                    s = wpt[k]
                    while '\n\n' in s:
                        s = s.replace('\n\n', '\n')
                    wpt[k] = s

        for trk in getlist(gpx, 'trk'):
            for trkseg in getlist(trk, 'trkseg'):
                trkpts = []
                last = None
                for trkpt in getlist(trkseg, 'trkpt'):
                    for k in ('@lat', '@lon'):
                        trkpt[k] = latlonfmt % (round(float(trkpt[k]), latlondigits))

                    # filter out duplicate points
                    pt = (trkpt['@lat'], trkpt['@lon'])
                    if pt != last:
                        trkpts.append(trkpt)
                    last = pt

                if trkpts:
                    trkseg['trkpt'] = trkpts

                    missing = []
                    for trkpt in trkpts:
                        ele = trkpt.get('ele') or '0'
                        if int(float(ele)) == 0:
                            missing.append((trkpt['@lat'], trkpt['@lon']))

                    elevations = get_elevations(missing)
                    for trkpt in trkpts:
                        pt = canon_point((trkpt['@lat'], trkpt['@lon']))
                        if pt in elevations:
                            trkpt['ele'] = elevations[pt]

        with open(f'dist/{basename}', 'w') as f:
            f.write(xmltodict.unparse(doc, pretty=True))

    with open('elevation-cache.json', 'w') as f:
        f.write(json.dumps(_elevation_cache, indent=2))

if __name__ == '__main__':
    main(sys.argv[1:])
