#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import os
import re

import psycopg2

class MapSearch():
    def __init__(self, host, port, user, passwd, dbname, sslmode):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.sslmode = sslmode

    def search(self, lat1, lon1, lat2, lon2):
        try:
            conn = psycopg2.connect(host=self.host,
                                    port=self.port,
                                    user=self.user,
                                    password=self.passwd,
                                    dbname=self.dbname,
                                    sslmode=self.sslmode)
        except Exception as e:
            print("pcycopg2.connect failed.")
            return None

        line = []
        line.append('%s %s' % (lon1, lat1))
        line.append('%s %s' % (lon1, lat2))
        line.append('%s %s' % (lon2, lat2))
        line.append('%s %s' % (lon2, lat1))
        line.append('%s %s' % (lon1, lat1))

        try:
            query = u"""
SELECT
  観光資源名,
  AVG(ST_Y(ST_Centroid("GEOM"))) lat,
  AVG(ST_X(ST_Centroid("GEOM"))) lon,
  都道府県名,
  所在地住所,
  CASE MIN(観光資源分類コード)
    WHEN 1 THEN '自然（行催事・イベント）'
    WHEN 2 THEN '歴史・文化'
    WHEN 3 THEN '温泉・健康'
    WHEN 4 THEN 'スポーツ・レクリエーション'
    WHEN 5 THEN '都市型観光-買物・食-'
    WHEN 6 THEN 'その他'
    ELSE ''
  END
FROM
  p12_14 a left outer join prefcode b
    on a.都道府県コード = b.都道府県コード
WHERE
  ST_Contains(ST_SetSRID(ST_MakePolygon('LINESTRING(%s)'::geometry), 4612), ST_Centroid("GEOM"))
GROUP BY
  観光資源名,
  都道府県名,
  所在地住所
ORDER BY
  digest(観光資源名 || 所在地住所, 'sha1')
LIMIT 101
""" % ','.join(line)
        except Excetption as e:
            print(e)

        results = []
        try:
            cur = conn.cursor()
            cur.execute(query)
            for r in cur.fetchall():
                results.append({'label': r[0], 'lat': r[1], 'lon': r[2], 'pref': r[3], 'address': r[4], 'category': r[5]})
        except Exception as e:
            print("fetchall() failed.")
            print(e)
            return None

        return results

if __name__ == '__main__':
    pghost = os.getenv("PGHOST")
    pgport = os.getenv("PGPORT")
    pguser = os.getenv("PGUSER")
    pgpass = os.getenv("PGPASS")
    dbname = os.getenv("DBNAME")
    m = MapSearch(host=pghost, port=pgport, user=pguser, passwd=pgpass, dbname=dbname, sslmode="require")
    print(json.dumps(m.search(35.09253662991008,138.36016149520879,36.16519333564296,140.99688024520879)))
