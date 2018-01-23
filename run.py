from routes import app
from config import app_secret_key
#to make gunicorn happy
application = app

# Run
if __name__ == '__main__':
	app.secret_key = app_secret_key
	app.run(debug=True)