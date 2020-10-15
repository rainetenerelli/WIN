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
            if 'eboard' not in session: # we don't need to check again if we have already set the value for eboard
                session['eboard'] = False
                if updateinfo.isEboard(conn, username):
                    session['eboard'] = True
            return render_template('main.html', username=username, eboard=session['eboard'])
        else:
            flash("Sorry, {} is not in the list of members. Please talk to an eboard member to be added.".format(username))
    # if we reach here, no one is logged in or the member is not valid so redirect to login page
    return render_template('login.html')

@app.route('/weapons/', methods=['GET','POST'])
def weapons():
    conn = dbi.connect()
    isEboard = not('eboard' not in session or not session['eboard'])
    if request.method == 'GET':
        allWeaponsList = filterweapons.getAllWeapons(conn)
        return render_template('showweapons.html', allWeaponsList = allWeaponsList, isEboard = isEboard)
    else:
        filterType = request.form.get("weapon-type")
        filteredWeaponsList = []
        if filterType == "select" or filterType == "all":
            filteredWeaponsList = filterweapons.getAllWeapons(conn)
        else:
            filteredWeaponsList = filterweapons.filterByType(conn, filterType)
        return render_template('showweapons.html', allWeaponsList = filteredWeaponsList, isEboard = isEboard)
    
@app.route('/checkout/', methods=['GET','POST'])
def checkout():
    conn = dbi.connect()
    if request.method == 'GET':
        available = updateinfo.getAllAvailableWeapons(conn)
        return render_template('checkoutform.html', weapons = available)
    else: # POST
        if 'CAS_USERNAME' not in session: # check to see if you are logged in
            flash("Sorry, you are not logged in. Please log in before checking out a weapon.")
            return redirect(url_for('index'))
        else: # if not logged in
            username = session['CAS_USERNAME']

            available = updateinfo.getAllAvailableWeapons(conn)
            # check to see if they selected a valid weapon
            if request.form["wid"] == "select":
                flash("You did not select a weapon. Please make sure to fill out all fields before submitting.")
                return render_template('checkoutform.html', weapons = available)
            
            wid = request.form["wid"]
            checkoutdate = request.form["checkoutdate"]

            # Validate wid: if the weapon is already checked out, flash an error and rerender the checkoutform
            # just in case multiple users are checking weapons out at simultaneously
            if not updateinfo.isWeaponAvailable(conn, wid):
                flash("Weapon {} is already checked out. Please select a different weapon.".format(wid))
                return render_template('checkoutform.html', weapons = available)

            try:
                updateinfo.checkout(conn, wid, username, checkoutdate)
            except:
                # Flash an error and rerender checkout form if the checkout fails
                flash("Uh oh! Updating the checkout failed.")
                return render_template('checkoutform.html', weapons = available)

            flash("Weapon {} successfully checked out out by {}".format(wid, username))
            return redirect(url_for('index'))
        

@app.route('/checkin/', methods=['GET','POST'])
def checkin():
    if 'CAS_USERNAME' in session: # check to see if you are logged in
        username = session['CAS_USERNAME']
        if request.method == 'GET':
            conn = dbi.connect()
            taken = updateinfo.getAllTakenWeapons(conn, username)
            return render_template('checkinform.html', weapons = taken)
        else: # POST
            conn = dbi.connect()
            wid = request.form["wid"]
            checkindate = request.form["checkindate"]
            weaponCon = request.form["condition"]
            checkoutdate = updateinfo.getCheckoutDate(conn, wid, username)
            try:
                updateinfo.checkin(conn, wid, username, checkoutdate.strftime("%Y-%m-%d"), checkindate, weaponCon)
            except:
                flash("Oh no! The checkin request failed")
                taken = updateinfo.getAllTakenWeapons(conn, username)
                return render_template('checkinform.html', weapons = taken)

            flash("Sucessessfully checked in weapon {}". format(wid))
            return redirect(url_for('index'))
    else: # if not logged in
        flash("Sorry, you are not logged in. Please log in before checking in a weapon.")
        return redirect(url_for('index'))

@app.route('/addmember/', methods=['GET','POST'])
def addmember():
    if 'eboard' not in session or not session['eboard']: 
        flash("You are not authorized to access the add member page")
        return redirect(url_for('index'))

    # If they reach here, the user is an eboard member
    if request.method == 'GET':
        return render_template('newmember.html')
    else: # POST
        conn = dbi.connect()
        name = request.form["newName"]
        username = request.form["newUsername"]
        try:
            updateinfo.addMember(conn, username, name)
            flash('Successfully added {} to the members database'.format(username))
        except:
            flash("Oops! This member could not be added. They may already be in the database.")
        return redirect(url_for('index'))

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


@app.route('/deleteWeaponAjax/', methods=['POST'])
def deleteWeaponAjax():
    if 'eboard' not in session or not session['eboard']: 
        flash("You are not authorized to delete a weapon")
        return redirect(url_for('index'))

    # If they reach here, the user is an eboard member
    conn = dbi.connect()
    wid = request.form["wid"]
    isWeaponAvailable = updateinfo.isWeaponAvailable(conn, wid)
    if (isWeaponAvailable):
        try:
            filterweapons.removeWeapon(conn, wid)
            flash('Successfully deleted weapon {} from the database'.format(wid))
            return jsonify({'error': False, 'wid': wid})
        except Exception as err:
            flash('Oops! This weapon could not be deleted. Unknown Error.')
            return jsonify({'error': True, 'err': str(err)}) 
    else:
        flash('Oops! Weapon {} could not be deleted. It is already checked out.'.format(wid))
        return jsonify({'error': True}) 
    

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
