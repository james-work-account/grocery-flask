import json
import time
from distutils import util

from config import Config
from flask import Flask, request, render_template, flash, session
from form import ProductForm
from search import Search
from werkzeug.utils import redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config.from_object(Config)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['200 per day', '50 per hour', '1 per second']
    # default_limits=['1 per second']
)
socketio = SocketIO(app, logger=True, engineio_logger=True)


@app.before_first_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=2)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response


@app.errorhandler(429)
def ratelimit_handler(e):
    session['error'] = 'Too many requests! Wait before trying again'
    time.sleep(0.5)
    return redirect('/')


@app.route('/')
def home():
    check_and_clear_session()
    result = get_session_key('result', as_json=True)
    search_term = get_session_key('search_term')
    error = get_session_key('error', pop=True)
    form = ProductForm(product=search_term)
    return render_template('home.html', form=form, search_result=result, error=error)


@socketio.on('my event', namespace='/socket')
def test_message(message):
    emit('my response', {'data': message['data']})


@socketio.on('search', namespace='/socket')
def search_product(product):
    emit('searching start')
    try:
        print(product)
        search = Search(product['data'])
        for shop in search.shops:
            result = search.do_thing(shop)
            emit('result', {
                'shop_name': result.shop_name,
                'result': result.result
            })
        search.driver.close()
    finally:
        emit('searching stop')


@socketio.on('connect', namespace='/socket')
def test_connect():
    emit('connection successful', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/socket')
def test_disconnect():
    print('Client disconnected')


# @app.route('/post', methods=['POST'])
# @limiter.limit('2/minute')
# def get_data():
#     if request.form['product'].strip() != '':
#         session['search_term'] = request.form['product']
#         search_result = Search(request.form['product'])
#         search_result.search_all()
#         session['result'] = search_result.to_json()
#     return redirect('/')


def check_and_clear_session():
    try:
        clear_session_as_str = request.args.get('clear_session')
        if clear_session_as_str:
            b = bool(util.strtobool(clear_session_as_str))
            get_session_key('result', as_json=True, pop=b)
            get_session_key('search_term', pop=b)
    except ValueError:
        pass



def get_session_key(key, as_json: bool = False, pop: bool = False):
    try:
        res = json.loads(session[key]) if as_json else session[key]
        if pop:
            session.pop(key)
        return res
    except KeyError:
        return None


if __name__ == '__main__':
    import os

    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
