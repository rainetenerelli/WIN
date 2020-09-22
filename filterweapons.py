# Written by Elaney Cheng
import cs304dbi as dbi

def filterByType(conn, type):
    '''Returns the wid, type, and condition of weapons of the specified type
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''
        select wid,type,`condition`
        from weapons 
        where type=%s''',
                 [type])
    return curs.fetchall()
