#!/usr/bin/env python

import asyncio
import zlib
import sys
sys.path.append('..')

from ezmysql import ConnectionAsync


async def main():
    host = 'localhost'
    database = 'testdb'
    user = 'root'
    password = 'aidbadmin'
    # to create database
    db = ConnectionAsync(
        host,
        None,
        user,
        password,
    )
    sql = 'drop database if exists {}'.format(database)
    await db.execute(sql)
    sql = 'create database if not exists %s' % database
    await db.execute(sql)
    db.close()
    # to operate database
    db = ConnectionAsync(
        host,
        database,
        user,
        password,
    )

    sql = '''CREATE TABLE IF NOT EXISTS `simple` (
      `id` int unsigned NOT NULL AUTO_INCREMENT,
      `title` varchar(1000) CHARACTER SET utf8mb4 DEFAULT NULL,
      `text` mediumtext CHARACTER SET utf8mb4,
      `author` varchar(1000) NOT NULL DEFAULT 'Jim',
      `length` tinyint(3) unsigned NOT NULL DEFAULT '0',
      `bin` blob,
      PRIMARY KEY (`id`)
    ) ENGINE=MyISAM  DEFAULT CHARSET=utf8mb4 ;'''
    await db.execute(sql)

    # db.execute()...
    sql = "insert into simple(title, text) values(%s, %s)"
    title = 'ezultramysql'
    text = 'text\nez\r\nultramysql%%\\123,item of the first'
    r = await db.execute(sql, title, text)
    row = await db.get('select * from simple where id=%s' % r)
    assert row['title'] == title
    assert row['text'] == text

    print('## test WARNING-0')
    sql = 'update simple set title="%s" where id=1'
    r = await db.execute(sql, 'apple')
    row = await db.get('select title from simple where id=1')
    print('%s != %s' % (row['title'], 'apple'))
    assert row['title'] != 'apple'

    print('\n## db.get()...')
    row = await db.get('select * from simple limit %s', 1)
    for k, v in row.items():
        print('%s: %s' % (k, v))

    print('\n## high-level interface testing...')
    g = await db.table_has('simple', 'id', 3)
    print('is_ in:', g)
    bin_zip = 'this is zlib to compress string'
    updates = {
        'title': 'by_"update"_table()',
        'text': 'by_update_table()\n\rzzz',
        'length': 123,
        'bin': zlib.compress(bin_zip.encode('utf8'))
    }
    r = await db.table_update('simple', updates, 'id', 1)
    print('update_table:', r)
    r = await db.get('select * from simple where id=1')
    assert r['title'] == updates['title']
    assert r['text'] == updates['text']
    assert bin_zip == zlib.decompress(r['bin']).decode('utf8')

    print('\n## db.query()...')
    rows = await db.query('select * from simple where text like %s limit %s', '%item%', 10)
    for r in rows:
        for k, v in r.items():
            print('%s: %s' % (k, v))
        print('======================')
    db.close()
    print('testing succeed!')


if __name__ == '__main__':
    asyncio.run(main())
