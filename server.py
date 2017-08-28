from flask import Flask, render_template, request, jsonify, flash, url_for, redirect, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import bookType, book, author, Base
from passlib.hash import sha256_crypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date, timedelta
import json
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm.exc import NoResultFound
from oauth2client import client, crypt
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
from flask import session as login_session


app = Flask(__name__)

app.secret_key = 'super_secret_key'

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Books Catalogue"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return session.query(author).filter_by(id = int(user_id)).one()

@app.route('/')
@app.route('/index', methods = ['GET', 'POST'])
def mainPage():
	book_types = session.query(bookType).all()
	return render_template('index.html', book_types = book_types)

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		print "inside post"
		# Obtain authorization code
		code = request.data
		#print code
		#print CLIENT_ID
		try:
			oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
			oauth_flow.params['access_type'] = 'offline'
			oauth_flow.redirect_uri = 'postmessage'
			credentials = oauth_flow.step2_exchange(code)
			#print credentials
			#print credentials.access_token
		except (FlowExchangeError , Exception) as u:
			print u
			response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
			response.headers['Content-Type'] = 'application/json'
			return response

		# Check that id token is valid
		access_token = credentials.access_token
		#print credentials.id_token
		#print "\n"+credentials.access_token
		url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
				% access_token)
		h = httplib2.Http()
		result = json.loads(h.request(url, 'GET')[1])
		if result.get('error') is not None:
			response = make_response(json.dumps(result.get('error')), 500)
			response.headers['Content-Type'] = 'application/json'
			return response

		gplus_id = credentials.id_token['sub']
		#print result
		if result['user_id'] != gplus_id:
			response = make_response(
				json.dumps("Token's user ID doesn't match given user ID."), 401)
			response.headers['Content-Type'] = 'application/json'
			return response

		if result['issued_to'] != CLIENT_ID:
			response = make_response(
				json.dumps("Token's client ID does not match app's."), 401)
			response.headers['Content-Type'] = 'application/json'
			return response

		c_auser = session.query(author).filter_by(gid = gplus_id).count()

		if c_auser == 1:
			#print "user already created"
			auser = session.query(author).filter_by(gid = gplus_id).one()
			login_user(auser)
			login_session['access_token'] = access_token
			response = make_response(json.dumps('Login Successful'), 200)
			response.headers['Content-Type'] = 'application/json'
			return response
		else:
			try:
				#print "creating user"
				userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
				params = {'access_token': credentials.access_token, 'alt': 'json'}
				answer = requests.get(userinfo_url, params=params)
				data = answer.json()
				a_author = author(name = data['name'],
    										email = data['email'],
    										gid = gplus_id)
				session.add(a_author)
				session.commit()
				login_user(a_author)
				login_session['access_token'] = access_token
				response = make_response(json.dumps('Login Successful after creating user'), 200)
				response.headers['Content-Type'] = 'application/json'
				return response
			except Exception as e:
				session.rollback()
				print e
				return render_template('login.html')
	else:
		return render_template('login.html')

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
	token = login_session.get('access_token')
	if token:
		print token
		url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % token
		h = httplib2.Http()
		result = h.request(url, 'GET')[0]
		print result
		if result['status'] == '200':
			del login_session['access_token']
			logout_user()
			flash('User Successfully Loged out')
		else:
			del login_session['access_token']
			logout_user()
			flash("User Loged Out, To completly Revoke Basic Access Kindly Access Your Google Console")
	else:
		flash("User No Logged In")
	return redirect(url_for('mainPage'))

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)