#!/usr/bin/env python3

import datetime
import os
import traceback
import uuid
from functools import partial

from bottle import request, response, route, run, static_file, template, view

import lib

OUTPUT = f'{os.getcwd()}/output'

def _log(s='', logs=None):
    logs.append(s)

@route('/bdr', ['GET', 'POST'])
@view('bdr.html')
def index():
    ctx = {
        'logs': [],
        'logpath': None,
        'filename': None,
    }

    log = partial(_log, logs=ctx['logs'])

    if request.method == 'POST':
        upload = request.files.get('upload')
        if upload and upload.filename != 'empty':
            name, ext = os.path.splitext(upload.filename)
            if ext.lower() == '.gpx':
                now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%S.%f")
                os.makedirs(f'{OUTPUT}/{now}/out')
                fname = upload.filename
                fin = f'{OUTPUT}/{now}/{fname}'
                fpath = f'{now}/out/{fname}'
                fout = f'{OUTPUT}/{fpath}'
                logpath = f'{now}/log-{os.path.splitext(fname)[0]}.txt'
                logout = f'{OUTPUT}/{logpath}'
                upload.save(fin)
                try:
                    lib.process(fin, fout, log)
                    ctx['filename'] = fpath
                except Exception as e:
                    exc = traceback.format_exc()
                    print(exc)
                    log(exc)

                ctx['logpath'] = logpath
                with open(logout, 'w') as f:
                    f.write('\n'.join(ctx['logs']).strip() + '\n')
            else:
                log('Extension not allowed, must be gpx')
        else:
            log('File not found')

    return ctx

@route('/bdr/download/<filename:path>')
def download(filename):
    fname = os.path.abspath(os.path.join(OUTPUT, filename))
    assert fname.startswith(OUTPUT), 'Invalid path'

    if not os.path.isfile(fname):
        response.set_status(404)
        return 'Not Found'

    with open(fname) as f:
        response.set_header("Content-Disposition", f"attachment; filename={os.path.split(fname)[1]}")
        return f.read()

run(host='0.0.0.0', port=5050, reloader=True)
