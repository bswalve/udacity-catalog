#!/usr/bin/python
from flask import Flask, flash, render_template
from flask import request, redirect, url_for, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from databasesetup import Base, Item, Category, User
from functools import wraps
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('fb_client_secrets.json', 'r').read())['web']['app_id']
APPLICATION_NAME = "Brian's first app"

engine = create_engine(
        'sqlite:///catalogapp.db',
        connect_args={'check_same_thread': False}
)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all categories and latest 9 items
@app.route('/')
@app.route('/catalog')
def showCategories():
    itemcount = session.query(Item).order_by(Item.category_id).count()
    items = session.query(Item).order_by(Item.id.desc()).limit(9)
    categories = session.query(Category).all()
    return render_template(
        'categories.html', categories=categories, items=items
    )


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("Please login to add or edit cataglog items")
            return redirect('/')
    return decorated_function


# Show items for specific category
@app.route('/catalog/<int:category_id>/items')
def showItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    itemcount = session.query(Item).filter_by(category_id=category_id).count()
    categories = session.query(Category).all()
    return render_template(
        'items.html', category=category, categories=categories,
        items=items, itemcount=itemcount
    )


# Show item
@app.route('/catalog/<int:item_id>')
def showItem(item_id):
    itemcount = session.query(Item).filter_by(id=item_id).count()
    if itemcount == 0:
        output = "There is no item %s in the database to show." % item_id
        output += "<a href='/'>Return Home</a>"
        return output
    else:
        item = session.query(Item).filter_by(id=item_id).one()
        return render_template('item.html', item=item)


# Edit a single item
@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def editItem(item_id):
    # make sure item_id is valid in the database
    itemcount = session.query(Item).filter_by(id=item_id).count()
    if itemcount == 0:
        output = "There is no item %s in the database to edit. " % item_id
        output += "<a href='/'>Return Home</a>"
        return output
    else:
        editedItem = session.query(Item).filter_by(id=item_id).one()
        if request.method == 'POST':
            # validate form is not empty
            name = request.form['name']
            if len(name) < 1:
                output = "The name of your item can not be blank, "
                output += "please enter a valid name.</br>"
                output += "<a href='/catalog/%s/edit'>" % item_id
                output += "Return to Form</a></br>"
                output += "<a href='/'>Return Home</a>"
                return output

            description = request.form['description']
            if len(description) < 5:
                output = "The description of your item should be at least 5"
                output += "characters, please enter a valid description.</br>"
                output += "<a href='/catalog/%s/edit'>" % item_id
                output += "Return to Form</a></br>"
                output += "<a href='/'>Return Home</a>"
                return output

            # make sure the user_id of logged in person
            # matches user_id stored when Item was created
            if editedItem.user_id == login_session['user_id']:
                if request.form['name']:
                    editedItem.name = request.form['name']
                if request.form['description']:
                    editedItem.description = request.form['description']
                if request.form['category']:
                    editedItem.category_id = request.form['category']
                session.add(editedItem)
                session.commit()
                return redirect(url_for('showCategories'))
            else:
                return redirect(url_for('showCategories'))
        else:
            item = session.query(Item).filter_by(id=item_id).one()
            items = session.query(Item).all()
            categories = session.query(Category).all()
            return render_template(
                'editItem.html', item=item, items=items,
                categories=categories, user_id=login_session['user_id']
            )


# POST new item to the database
@app.route('/catalog/item/new', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        item_user_id = login_session['user_id']

        name = request.form['name']
        if len(name) < 1:
            output = "The name of your item can not be blank, "
            output += "please enter a valid name.</br>"
            output += "<a href='/catalog/item/new'>Return to Form</a></br>"
            output += "<a href='/'>Return Home</a>"
            return output

        description = request.form['description']
        if len(description) < 5:
            output = "The description of your item should be at least, "
            output += "5 characters, please enter a valid description.</br>"
            output += "<a href='/catalog/item/new'>Return to Form</a></br>"
            output += "<a href='/'>Return Home</a>"
            return output

        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=item_user_id
        )
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newItem.html')


# Delete a specific item
@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    if request.method == 'POST':
        itemToDelete = session.query(Item).filter_by(id=item_id).one()
        # make sure the user_id of logged in person
        # matches user_id stored when Item was created
        if itemToDelete.user_id == login_session['user_id']:
            session.delete(itemToDelete)
            session.commit()
            return redirect(url_for('showCategories'))
        else:
            return redirect(url_for('showCategories'))
    else:
        # make sure item_id is valid in the database
        itemcount = session.query(Item).filter_by(id=item_id).count()
        if itemcount == 0:
            output = "There is no item %s in the database to delete." % item_id
            output += "<a href='/'>Return Home</a>"
            return output
        else:
            item = session.query(Item).filter_by(id=item_id).one()
            return render_template(
                'delete.html', item=item, user_id=login_session['user_id']
            )


# API Endpoint for GET Request of Categories and Items
@app.route('/catalog.json')
def returnAllJSON():
    categories = session.query(Category).order_by(Category.id).all()
    items = session.query(Item).order_by(Item.category_id).all()
    return jsonify(
        Categories=[i.serialize for i in categories],
        Items=[i.serialize for i in items]
    )


# API Endpoint for GET Request of single Item
@app.route('/catalog/item/<int:item_id>/JSON')
def returnItemJSON(item_id):
    # make sure item_id is valid in the database
    itemcount = session.query(Item).filter_by(id=item_id).count()
    if itemcount == 0:
        output = "There is no item %s in the database." % item_id
        output += "<a href='/'>Return Home</a>"
        return output
    else:
        item = session.query(Item).filter_by(id=item_id).one()
        return jsonify(Item=item.serialize)


# API Endpoint for GET Request of single Category
@app.route('/catalog/category/<int:id>/JSON')
def returnCategoryJSON(id):
    catcount = session.query(Category).filter_by(id=id).count()
    if catcount == 0:
        output = "There is no category %s in the database." % id
        output += "<a href='/'>Return Home</a>"
        return output
    else:
        category = session.query(Category).filter_by(id=id).one()
        return jsonify(Category=category.serialize)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Create error page
@app.route('/error')
def showError():
    flash("Error page")
    return render_template('error.html')


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['facebook_id']
    return redirect(url_for('showCategories'))


# User Helper Functions
def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'my_final'
    # app.debug = True
    app.run(host='0.0.0.0', port=8000)
