from flask import abort
from flask import Flask
from flask import make_response
from flask import redirect



app = Flask(__name__)


@app.route('/')
def index():
	response = make_response('<h1>This document carries a cookie!<h1>')
	response.set_cookie('answer', '42')
	return response


@app.route('/sky')
def sky_redirect():
	return redirect ('http://www.skydns.ru', code=302)


if __name__ == '__main__':
	app.run()
