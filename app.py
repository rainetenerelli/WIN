'''
Project: Wushu Inventory Ninja
Project Description: Weapons Database for Wellesley Wushu
Authors: Elaney Cheng, Christine Lam, Raine Tenerelli, Eugenia Zhang
Course: CS304 Fall T1 2020
'''
# File Author: Christine Lam

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)

import cs304dbi as dbi
import filterweapons
import updateinfo
import random

app = Flask(__name__)

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('main.html')
    elif request.method == 'POST':
        username = request.form['username']
        # check if username is correct
        # redirect to either general or eboard
        if (username == 'eboard'):
            return redirect(url_for('eboard'))
        elif (username == 'genmem'):
            return redirect(url_for('genmem'))
        else: # incorrect username
            flash("Wrong username. Please try again.")
            return redirect(url_for('index'))

@app.route('/genmem/')
def genmem():
    return render_template('generalmember.html')

@app.route('/eboard/')
def eboard():
    return render_template('eboardmember.html')

@app.route('/weapons/', methods=['GET','POST'])
def weapons():
    if request.method == 'GET':
        conn = dbi.connect()
        allWeaponsList = filterweapons.getAllWeapons(conn)
        return render_template('showweapons.html', allWeaponsList = allWeaponsList)
    else:
        conn = dbi.connect()
        filterType = request.form.get("weapon-type")
        filteredWeaponsList = filterweapons.filterByType(conn,filterType)
        return render_template('showweapons.html', allWeaponsList = filteredWeaponsList)
    
@app.route('/checkout/')
def checkout():
    return render_template('checkoutform.html')

@app.route('/checkin/')
def checkin():
    return render_template('checkinform.html')

@app.route('/addmember/')
def addmember():
    return render_template('newmember.html')

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    dbi.use('uwushu_db')

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)

