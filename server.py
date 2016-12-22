#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, request, redirect, abort, Response, make_response
import json
import os
import re

import pgmap

pghost = os.getenv("PGHOST")
pgport = os.getenv("PGPORT")
pguser = os.getenv("PGUSER")
pgpass = os.getenv("PGPASS")
dbname = os.getenv("DBNAME")

app = Flask(__name__)

@app.route('/map/loc', methods=['GET'])
def map_loc():
    m = pgmap.MapSearch(host=pghost, port=pgport, user=pguser, passwd=pgpass, dbname=dbname, sslmode="require")
    
    d = request.args.get('latlon').split(',')
    return json.dumps(m.search(d[0], d[1], d[2], d[3]))

@app.route('/')
def index():
    return redirect('/static/maps/index.html')

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))
