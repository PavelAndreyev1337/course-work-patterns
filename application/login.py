# circular import because its needed for modular code. I know its ugly. Shhh.
from application import app
# imports for various flask functions
from flask import request, render_template, redirect, flash, session
from os import urandom  # generating salt
import hashlib  # library for hashing (fairly self-explanatory :P)
from .helper_functions import *
import binascii


# LOGIN THE USER
@app.route('/login/', methods=['POST'])
def login():
    # get form information
    formData = request.form
    # validation
    if formData['username'] == "":
        flash("The username field is required.")
        return redirect("/")
    if formData['password'] == "":
        flash("The password field is required.")
        return redirect("/")
    # get data from database
    data = query_db("SELECT password, salt, isTeacher, id FROM people WHERE username=? LIMIT 1", [
                    formData['username']])
    # make sure username is right
    if data == []:
        flash("Your username was incorrect.")
        return redirect("/")
    # check the password
    if data[0][0] == hashlib.md5((data[0][1] + formData['password']).encode()).hexdigest():
        # correct password
        session['isTeacher'] = data[0][2]
        session['id'] = data[0][3]
        # if student, redirect to students page
        if session['isTeacher'] == 0:
            return redirect("/students/")
        # else they are a teacher, redirect to teachers page
        else:
            return redirect("/teachers/")
    flash("Your password was incorrect.")
    return redirect("/")


# REGISTER THE USER
@app.route('/register/', methods=['GET', 'POST'])
def register():
    # form data is GET, so render template
    if request.method == 'GET':
        return render_template('register.html')
    # request method is POST, so do everything
    formData = request.form
    # form validation
    if formData['username'] == "" or formData['password'] == "" or formData['name'] == "" or formData['email'] == "":
        return "All text fields are required"
    if not 'isTeacher' in formData:  # if is teacher wasn't selected
        isTeacher = 0  # they aren't a teacher...
    else:
        isTeacher = 1  # they are a teacher!
    # hash w/salt
    salt = binascii.hexlify(urandom(32)).decode()
    password = hashlib.md5((salt + formData['password']).encode()).hexdigest()
    insert_db("INSERT INTO people (isTeacher, username, password, salt, name, email) VALUES (?, ?, ?, ?, ?, ?)", [
              isTeacher, formData['username'], password, salt, formData['name'], formData['email']])
    flash("The entry was created")
    return redirect("/register/")
