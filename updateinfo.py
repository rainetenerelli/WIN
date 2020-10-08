'''
Project: Wushu Inventory Ninja
Project Description: Weapons Database for Wellesley Wushu
Authors: Elaney Cheng, Christine Lam, Raine Tenerelli, Eugenia Zhang
Course: CS304 Fall T1 2020
'''

import cs304dbi as dbi

# Used to validate if this weapon can be checked out
def isWeaponAvailabe(conn, wid):
    '''
    Return True if the weapon with wid is not checked out, False otherwise
    '''
    curs = dbi.cursor(conn)
    # Check if the weapon is currently checked out
    res = curs.execute('''select wid from checkedout where checkindate is null and wid=%s''', [wid])
    return res == 0

#  Can use for dropdown, or write alternative
def getAllAvailableWeapons(conn):
    '''
    Return the wid, type, and condition of all weapons that are available to checkout of any type
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                select wid,type,`condition` from weapons 
                where wid not in (select wid from checkedout where checkindate is null)''')
    return curs.fetchall()

#  Can use for dropdown, for checking in
def getAllTakenWeapons(conn):
    '''
    Return the wid, type, and condition of all weapons that are available to checkin of any type
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                select wid,type,`condition` from weapons 
                where wid in (select wid from checkedout where checkindate is null)''')
    return curs.fetchall()

#  Possibly may not need
def getAvailableWeaponsOfType(conn, type):
    '''
    Return the wid of all weapons that are available to checkout of specified type
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                select wid from weapons 
                where type=%s and wid not in (select wid from checkedout where checkindate is null)''',
                [type])
    return curs.fetchall()

def checkout(conn, wid, username, checkoutdate):
    '''
    Update the checkout table with the new checkout info
    '''
    curs = dbi.cursor(conn)
    try:
        curs.execute('''insert into checkedout(wid, username, checkoutdate, checkindate) values (%s, %s, %s)''', 
                    [wid, username, checkoutdate])
        conn.commit()
    except:
        print("Uh oh! Adding the checkout information failed.")

def getCheckoutDate(conn, wid, username):
    '''
    Get the checkout date of an (unreturned) request for a member
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select checkoutdate from checkedout where wid=%s and username=%s and checkindate is null''',
                [wid, username])
    return curs.fetchone()['checkoutdate']

def checkin(conn, wid, username, checkoutdate, checkindate):
    '''
    Update the checkout request with the checkin date
    '''
    curs = dbi.cursor(conn)
    curs.execute('''update checkedout set checkindate=%s where wid=%s and username=%s and checkoutdate=%s''', 
                [checkindate, wid, username, checkoutdate])
    conn.commit()

def isMember(conn, username):
    '''
    Returns True if there is a member with the specified username, False otherwise
    '''
    curs = dbi.cursor(conn)
    res = curs.execute('''select username from members where username=%s''', [username])
    return res > 0

def addMember(conn, username, name):
    '''
    Add a new member to the members table
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into members(username, name) values (%s, %s)''', [username, name])
    conn.commit()
        