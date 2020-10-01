'''
Project: Wushu Inventory Ninja
Project Description: Weapons Database for Wellesley Wushu
Authors: Elaney Cheng, Christine Lam, Raine Tenerelli, Eugenia Zhang
Course: CS304 Fall T1 2020
'''

import cs304dbi as dbi

def getAllWeapons(conn):
    '''
    Returns the wid, type, and condition of all weapons
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select wid,type,`condition` from weapons''')
    return curs.fetchall()

def filterByType(conn, type):
    '''
    Returns the wid, type, and condition of weapons of the specified type
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select wid,type,`condition` 
        from weapons 
        where type=%s''',
                 [type])
    return curs.fetchall()
