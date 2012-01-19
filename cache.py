#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of anonshort
#
#  anonshort is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  anonshort is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with anonshort  If not, see <http://www.gnu.org/licenses/>.
#
# (C) 2012- by Stefan Marsiske, <stefan.marsiske@gmail.com>

## 12:18 <@dnet> szerintem megoldhato crypto modszerrel ;)
## 12:19 <@dnet> A = sha512(shorturl)
## 12:20 <@dnet> A-t felbontjuk ket 256 byte-os reszre: A = B + C
## 12:20 <@dnet> s/byte-o/bite/
## 12:21 <@dnet> feloldas utan letaroljuk a B -> AES(key=C, data=longurl) hozzarendelest
## 12:21 <@dnet> innentol nem allithato vissza semmi a hozzarendelesek birtokaban
## 12:21 <@dnet> viszont ha jon egy keres, A, B, C eloallithato
## 12:21 <@dnet> es B+C birtokaban elokeritheto, melyik URL kell, es feloldhato a titkositas
## 12:22 <@dnet> velemeny? ;)
## 12:33 <@dnet> szoval nem sima sha512, hanem letarolunk egy S salt erteket, es A = sha512(shorturl) helyett A = HMAC(key=S, algo=SHA512, data=shorturl)

from __future__ import with_statement
import hmac, hashlib
from Crypto.Cipher import AES
from Crypto import Random
from contextlib import closing
from base64 import b64encode, b64decode
import sqlite3

SALT="3j3,xiDS"
db = sqlite3.connect("cache.db")
CREATE_SQL = """
CREATE TABLE urlcache (key TEXT PRIMARY KEY, value TEXT);
"""

class sha512:
    digest_size = 64
    def new(self, inp=''):
        return hashlib.sha512(inp)

def get_key(key,salt=SALT):
    A = hmac.new(salt, key, sha512())
    return (A.hexdigest()[:64],
            A.digest()[32:])

def encrypt(C, value):
    # encrypt value with second half of MAC
    bsize=len(C)
    cipher = AES.new(C, AES.MODE_OFB)
    # pad value
    value += chr(0x08) * (-len(value) % bsize)
    return b64encode(''.join([cipher.encrypt(value[i*bsize:(i+1)*bsize])
                              for i in range(len(value)/bsize)]))

def decrypt(C, value):
    # decode value
    value=b64decode(value)
    cipher = AES.new(C, AES.MODE_OFB)
    bsize=len(C)
    return ''.join([cipher.decrypt(value[i*bsize:(i+1)*bsize])
                    for i in range(len(value)/bsize)]).rstrip(chr(0x08))

def set(key,value):
    # ignore already inserted items
    if get(key): return

    # calculate keys
    B, C = get_key(key)
    ciphertext = encrypt(C, value)
    # store B: base64(aes(C,value))
    query_db('INSERT INTO urlcache (key, value) VALUES (?, ?)',
             (B, ciphertext))

def get(key):
    # calculate keys
    B, C = get_key(key)
    value = query_db("SELECT value FROM urlcache WHERE key == ? LIMIT 1", (B,))
    if value:
        return decrypt(C, value)

def initdb():
    cursor = db.cursor()
    cursor.executescript(CREATE_SQL)

def query_db(query, params=[]):
    with closing(db.cursor()) as cursor:
        cursor.execute(query, params)
        db.commit()
        return (cursor.fetchone() or [None])[0]

def salt(key, value):
    salt_size=3
    salt=Random.get_random_bytes(salt_size)
    hash=get_key(key,salt)
    print bytearray(salt), hash
    ciphertext=encrypt(hash[1],value)
    print decrypt(hash[1],ciphertext)

    for s in xrange(pow(2,salt_size*8)):
        res=[]
        for i in xrange(salt_size):
            res.append(s & 0xff)
            s=s >> 8
        s=bytearray(res)
        k=get_key(key,s)
        #value = query_db("SELECT value FROM urlcache WHERE key == ? LIMIT 1", (B,))
        #if value:
        #    print i
        #    return value
        if k[0]==hash[0]:
            print bytearray(s), k
            print decrypt(k[1],ciphertext)
            break

if __name__ == "__main__":
    #initdb()
    print salt("http://bit.ly/xJ5pK2", "ctrlc.hu")
