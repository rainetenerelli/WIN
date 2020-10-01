'''
Project: Wushu Inventory Ninja
Project Description: Weapons Database for Wellesley Wushu
Authors: Elaney Cheng, Christine Lam, Raine Tenerelli, Eugenia Zhang
Course: CS304 Fall T1 2020
'''
# File Author: Elaney Cheng

import cs304dbi as dbi

def getAllAvailableWeapons(conn):
    '''
    Return the wid, type, and condition of all weapons that are available to checkout of any type
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
                select wid,type,`condition` from weapons 
                where wid not in (select wid from checkedout where checkindate is null)''')
    return curs.fetchall()

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

def checkout(conn, wid, email, checkoutdate):
    '''
    Update the checkout table with the new checkout info
    '''
    curs = dbi.cursor(conn)
    try:
        curs.execute('''insert into checkedout(wid, email, checkoutdate) values (%s, %s, %s)''', 
                    [wid, email, checkoutdate])
        conn.commit()
    except:
        print("Uh oh! Adding the checkout information failed.")

def getCheckoutDate(conn, wid, email):
    '''
    Get the checkout date of an (unreturned) request for a member
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select checkoutdate from checkedout where wid=%s and email=%s and checkindate is null''',
                [wid, email])
    return curs.fetchone()

def checkin(conn, wid, email, checkoutdate, checkindate):
    '''
    Update the checkout request with the checkin date
    '''
    curs = dbi.cursor(conn)
    try:
        curs.execute('''update checkedout set checkindate=%s where wid=%s and email=%s and checkoutdate=%s''', 
                    [checkindate, wid, email, checkoutdate])
        conn.commit()
    except:
        print("Uh oh! Updating the checkout failed.")

def getMembers(conn):
    '''
    Returns the email addresses of all members in the table
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select email from members''')
    return curs.fetchall()

def addMember(conn, email, name):
    '''
    Add a new member to the members table
    '''
    curs = dbi.dict_cursor(conn)
    try:
        curs.execute('''insert into members(email, name) values (%s, %s)''', 
                    [email, name])
        conn.commit()
    except:
        print("Oops! This member could not be added. They may already be in the database.")