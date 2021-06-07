from app import app
import flask_login
import flask
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_user, UserMixin

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    pass

users = {'1': {'password': 'secret'}}

@login_manager.request_loader
def request_loader(request):
    id = request.form.get('id')
    print("ID: ", id)
    if id not in users:
        return

    user = User()
    user.id = id

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[id]['password']

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('login.html', msg="")

@login_manager.user_loader
def user_loader(id):
    if id not in users:
        return
    user = User()
    user.id = id
    return user




@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('login.html', msg="You have been logged out. ")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')
    if flask.request.form['password'] == users['1']['password']:
        user = User()
        user.id = '1'
        flask_login.login_user(user)
        return redirect('/view')
    return render_template('login.html', msg="The password is incorrect.")
