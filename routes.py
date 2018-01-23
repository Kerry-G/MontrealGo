import random
from flask import Flask, render_template, url_for, request
from bot import Bot
from Utils.reddit.reddit import getImage, getNews, getHistorical


app = Flask(__name__)
botController = Bot()

def main():
    app.run()

if __name__ == "__main__":
    main()

@app.route("/", methods=['GET', 'POST'])
def botRoute():
    return botController.receive_message()

# Policy page
@app.route("/policy/")
def privacy_page():
    return "<h1 style='font-size: 24px;'>We don't share or store your data. Period.</h1>"

# DEBUG IMAGE
@app.route('/debug')
def debug():
    return render_template('debug.html',image=getHistorical())


if __name__ == "__main__":
    app.run()
