# Written by Elaney Cheng
import cs304dbi as dbi

def checkOut(conn, wid, email, checkoutdate):
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

def checkIn(conn, wid, email, checkoutdate, checkindate):
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