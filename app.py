'''
Project: Wushu Inventory Ninja
Project Description: Weapons Database for Wellesley Wushu
Authors: Elaney Cheng, Christine Lam, Raine Tenerelli, Eugenia Zhang
Course: CS304 Fall T1 2020
'''
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
import filterweapons
import updateinfo

@app.route('/')
def index():
    return render_template('templates/base.html')

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
