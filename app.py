'''
Project: Wushu Inventory Ninja
Project Description: Weapons Database for Wellesley Wushu
Authors: Elaney Cheng, Christine Lam, Raine Tenerelli, Eugenia Zhang
Course: CS304 Fall T1 2020
'''
# File Author: Christine Lam

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
import filterweapons
import updateinfo
import random

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
        return render_template('templates/base.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # check if username is correct
        # redirect to either general or eboard

@app.route('/genmem/')
def genmem():
    return render_template('templates/generalmember.html')

@app.route('/eboard/')
def eboard():
    return render_template('templates/eboard.html')

@app.route('/weapons/', methods=['GET','POST'])
def weapons():
    if request.method == 'GET':
        conn = dbi.connect()
        allWeaponsList = filterweapons.getAllWeapons(conn)
        return render_template('templates/showweapons.html', allWeaponsList)
    else:
        filterType = request.form.get("weapon-type")
        filteredWeaponsList = filterweapons.filterByType(conn,filterType)
        return render_template('templates/showweapons.html', filteredWeaponsList)
    
@app.route('/checkout/')
def checkout():
    return render_template('templates/checkoutform.html')

@app.route('/checkin/')
def checkin():
    return render_template('templates/checkinform.html')

@app.route('/addmember/')
def addmember():
    return render_template('templates/newmember.html')

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
