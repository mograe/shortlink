import sqlite3
import hash
from random import randint

def check_hashling(hashlink):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"SELECT hashlink from shortlink WHERE hashlink = '{hashlink}'")
    if sql_cur.fetchall() == []:
        return True
    else:
        return False

def return_links(user_id):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"SELECT hashlink, link from shortlink WHERE user_id = {user_id}")
    return sql_cur.fetchall()

def hashlink(user_id,link):
    hash_user_id = hash.getHash(user_id)
    hash_url = hash.getHash(link)
    dhashlink = hash_url+hash_user_id
    hl = dhashlink
    while(not check_hashling(hl)):
        i = randint(0,100000)
        hl += hash.getHash(1)[0:2]
    return hl


def shortlink(user_id,link):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    hl = hashlink(user_id,link)
    sql_cur.execute(f"INSERT INTO shortlink (user_id,link,hashlink) VALUES ({user_id},'{link}','{hl}')")
    db.commit()

def add_name(user_id,link,name):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"INSERT INTO shortlink (user_id,link,hashlink) VALUES ({user_id},'{link}','{name}')")
    db.commit()

def ret_sl(user_id,link):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"SELECT hashlink from shortlink WHERE user_id = {user_id} AND link = '{link}'")
    return sql_cur.fetchall()[0][0]

def ret_fulllink(short_link):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"SELECT link from shortlink WHERE hashlink = '{short_link}'")
    return sql_cur.fetchall()[0][0]

def check_name(name):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"SELECT hashlink from shortlink WHERE hashlink = '{name}'")
    if sql_cur.fetchall() == []:
        return False
    else:
        return True

def rename_link(name,shortlink,user_id):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"UPDATE shortlink SET hashlink='{name}' WHERE hashlink='{shortlink}' and user_id = {user_id}")
    db.commit()

def delete_link(shortlink,user_id):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"DELETE from shortlink WHERE user_id={user_id} and hashlink='{shortlink}'")
    db.commit()

def get_slink(user_id,number):
    db = sqlite3.connect("db.db")
    sql_cur = db.cursor()
    sql_cur.execute(f"SELECT hashlink, link from shortlink WHERE user_id = {user_id}")
    return sql_cur.fetchall()[number][0]
