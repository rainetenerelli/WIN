'''
Project: Wushu Inventory Ninja
Project Description: Weapons Database for Wellesley Wushu
Authors: Elaney Cheng, Christine Lam, Raine Tenerelli, Eugenia Zhang
Course: CS304 Fall T1 2020
'''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify,
                   abort)
from werkzeug.utils import secure_filename
from os import listdir
import cs304dbi as dbi
import filterweapons
import updateinfo
import random


app = Flask(__name__)
app.config['UPLOAD_PATH'] = 'static/images'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.config['MAX_CONTENT_LENGTH'] = 2048 * 2048

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

@app.route('/logged_in/')
def logged_in():
    return redirect(url_for('index'))

@app.route('/')
def index():
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
        conn = dbi.connect()
        if updateinfo.isMember(conn, username):
            return render_template('main.html', username=username)
        else:
            flash("Sorry, {} is not in the list of members. Please talk to an eboard member to be added.".format(username))
    # if we reach here, no one is logged in or the member is not valid so redirect to login page
    return render_template('login.html')

@app.route('/weapons/', methods=['GET','POST'])
def weapons():
    if request.method == 'GET':
        conn = dbi.connect()
        allWeaponsList = filterweapons.getAllWeapons(conn)
        return render_template('showweapons.html', allWeaponsList = allWeaponsList)
    else:
        conn = dbi.connect()
        filterType = request.form.get("weapon-type")
        filteredWeaponsList = []
        if filterType == "select" or filterType == "all":
            filteredWeaponsList = filterweapons.getAllWeapons(conn)
        else:
            filteredWeaponsList = filterweapons.filterByType(conn, filterType)
        return render_template('showweapons.html', allWeaponsList = filteredWeaponsList)
    
@app.route('/checkout/', methods=['GET','POST'])
def checkout():
    if request.method == 'GET':
        conn = dbi.connect()
        available = updateinfo.getAllAvailableWeapons(conn)
        return render_template('checkoutform.html', weapons = available)
    else: # POST
        if 'CAS_USERNAME' in session: # check to see if you are logged in
            username = session['CAS_USERNAME']
            conn = dbi.connect()
            wid = request.form["wid"]
            checkoutdate = request.form["checkoutdate"]

            # Replace with 
            # Validate wid: if the weapon is already checked out, flash an error and rerender the checkoutform
            if not updateinfo.isWeaponAvailabe(conn, wid):
                flash("Weapon {} is already checked out. Please select a different weapon.".format(wid))
                return render_template('checkoutform.html')

            # Validate email: if the member does not exist, redirect to the add member page
            if not updateinfo.isMember(conn, username):
                flash("{} is not in the member database".format(username))
                return redirect(url_for('addmember'))
            try:
                updateinfo.checkout(conn, wid, username, checkoutdate)
            except:
                # Flash an error and rerender checkout form if the checkout fails
                flash("Uh oh! Updating the checkout failed.")
                return render_template('checkoutform.html')

            flash("Weapon {} successfully checked out out by {}".format(wid, username))
            return redirect(url_for('index'))
        else: # if not logged in
            flash("Sorry, you are not logged in. Please log in before checking out a weapon.")
            return redirect(url_for('index'))
        

@app.route('/checkin/', methods=['GET','POST'])
def checkin():
    if request.method == 'GET':
        conn = dbi.connect()
        taken = updateinfo.getAllTakenWeapons(conn)
        print(taken)
        return render_template('checkinform.html', weapons = taken)
    else: # POST
        if 'CAS_USERNAME' in session: # check to see if you are logged in
            username = session['CAS_USERNAME']
            conn = dbi.connect()
            # For now, assume all weapon ids and emails are valid
            wid = request.form["wid"]
            checkindate = request.form["checkindate"]
            checkoutdate = updateinfo.getCheckoutDate(conn, wid, username)
            try:
                updateinfo.checkin(conn, wid, username, checkoutdate.strftime("%Y-%m-%d"), checkindate)
            except:
                flash("Oh no! The checkin request failed")
                taken = updateinfo.getAllTakenWeapons(conn)
                return render_template('checkinform.html', weapons = taken)

            flash("Sucessessfully checked in weapon {}". format(wid))
            return redirect(url_for('index'))
        else: # if not logged in
            flash("Sorry, you are not logged in. Please log in before checking in a weapon.")
            return redirect(url_for('index'))

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

@app.route('/images/')
def images():
   image_arr = os.listdir(app.config['UPLOAD_PATH'])
   return render_template('images.html', image_arr = image_arr)
	
@app.route('/images/', methods = ['POST'])
def upload_file():
    uploaded_file = request.files['image_file']
    filename = secure_filename(uploaded_file.filename)
    image_arr = os.listdir(app.config['UPLOAD_PATH'])
    # check that image exists
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            # checking if valid extension
            flash("Not a valid upload. Must be .jpg .png or .jpeg")
            return render_template('images.html', image_arr = image_arr)
        # checking if image already exists
        if filename in image_arr:
            flash("This image name is already in use. You might be trying to " + 
            "upload an existing image.")
            return render_template('images.html', image_arr = image_arr)
        # save image
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash("Image sucessfully uploaded. Yeehaw.")
    return redirect(url_for('images'))

@app.route('/images/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

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
