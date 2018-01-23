import random
from flask import Flask, render_template, url_for, request
from bot import Bot_Controller
from Utils.reddit.reddit import getImage, getNews, getHistorical


app = Flask(__name__)
botController = Bot_Controller()




@app.route("/", methods=['GET', 'POST'])
def botRoute():
	if request.method == 'GET' or request.method == 'POST':
    	return botController.receive_message()
    else:
    	return "<p>Main Page Content</p>"

# Policy page
@app.route("/policy/")
def privacy_page():
    return "<h1 style='font-size: 24px;'>We don't share or store your data. Period.</h1>"


# DEBUG
@app.route('/debug')
def debug():
    return render_template('debug.html', image=getHistorical())


