'''
Project: Wushu Inventory Ninja
Project Description: Weapons Database for Wellesley Wushu
Authors: Elaney Cheng, Christine Lam, Raine Tenerelli, Eugenia Zhang
Course: CS304 Fall T1 2020
'''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)

import cs304dbi as dbi
import filterweapons
import updateinfo
import random

app = Flask(__name__)

app.secret_key = 'uwu'
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# CAS setup
from flask_cas import CAS

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/logged_in/')
def logged_in():
    flash('Successfully logged in!')
    return redirect(url_for('index'))

@app.route('/home/')
def index():
    if '_CAS_TOKEN' in session:
        token = session['_CAS_TOKEN']
    if 'CAS_ATTRIBUTES' in session:
        attribs = session['CAS_ATTRIBUTES']
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
        conn = dbi.connect()
        if updateinfo.isMember(conn, username):
            return render_template('main.html', username=username)
        else:
            flash("Sorry, {} is not in the list of members. Please talk to an eboard member to be added.".format(username))
    # if we reach here, no one is logged in or the member is not valid
    return redirect(url_for('login'))

@app.route('/weapons/', methods=['GET','POST'])
def weapons():
    if request.method == 'GET':
        conn = dbi.connect()
        allWeaponsList = filterweapons.getAllWeapons(conn)
        return render_template('showweapons.html', allWeaponsList = allWeaponsList)
    else:
        conn = dbi.connect()
        filterType = request.form.get("weapon-type")
        filterTypeSplit = filterType.split(" ")
        filteredWeaponsList = []
        for fType in filterTypeSplit:
            filteredWeaponsList += filterweapons.filterByType(conn,fType)
        return render_template('showweapons.html', allWeaponsList = filteredWeaponsList)
    
@app.route('/checkout/', methods=['GET','POST'])
def checkout():
    if request.method == 'GET':
        return render_template('checkoutform.html')
    else: # POST
        conn = dbi.connect()
        wid = request.form["wid"]
        email = request.form["email"]
        checkoutdate = request.form["checkoutdate"]

        # Validate wid: if the weapon is already checked out, flash an error and rerender the checkoutform
        if not updateinfo.isWeaponAvailabe(conn, wid):
            flash("Weapon {} is already checked out. Please select a different weapon.".format(wid))
            return render_template('checkoutform.html')

        # Validate email: if the member does not exist, redirect to the add member page
        if not updateinfo.isMember(conn, email):
            flash("{} is not in the member database".format(email))
            return redirect(url_for('addmember'))
        try:
            updateinfo.checkout(conn, wid, email, checkoutdate)
        except:
            # Flash an error and rerender checkout form if the checkout fails
            flash("Uh oh! Updating the checkout failed.")
            return render_template('checkoutform.html')

        flash("Weapon {} successfully checked out out by {}".format(wid, email))
        return redirect(url_for('wushu'))
        

@app.route('/checkin/', methods=['GET','POST'])
def checkin():
    if request.method == 'GET':
        return render_template('checkinform.html')
    else: # POST
        conn = dbi.connect()
        # For now, assume all weapon ids and emails are valid
        wid = request.form["wid"]
        email = request.form["email"]
        checkindate = request.form["checkindate"]
        checkoutdate = updateinfo.getCheckoutDate(conn, wid, email)

        try:
            updateinfo.checkin(conn, wid, email, checkoutdate.strftime("%Y-%m-%d"), checkindate)
        except:
            flash("Oh no! The checkin request failed")
            return render_template('checkinform.html')

        flash("Sucessessfully checked in weapon {}". format(wid))
        return redirect(url_for('wushu'))

@app.route('/addmember/', methods=['GET','POST'])
def addmember():
    if request.method == 'GET':
        return render_template('newmember.html')
    else: # POST
        conn = dbi.connect()
        name = request.form["newName"]
        email = request.form["newEmail"]
        try:
            updateinfo.addMember(conn, email, name)
        except:
            flash("Oops! This member could not be added. They may already be in the database.")
        return redirect(url_for('checkout'))

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    dbi.use('uwushu_db')

if __name__ == '__main__':
    import sys, os

    if len(sys.argv) > 1:
        port=int(sys.argv[1])
        if not(1943 <= port <= 1952):
            print('For CAS, choose a port from 1943 to 1952')
            sys.exit()
    else:
        port=os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
# if __name__ == '__main__':
#     import sys, os
#     if len(sys.argv) > 1:
#         port = int(sys.argv[1])
#         assert(port>1024)
#     else:
#         port = os.getuid()
#     app.debug = True
#     app.run('0.0.0.0',port)

