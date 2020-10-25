import json
import time
from datetime import timedelta
from distutils import util

from flask import Flask, request, render_template, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit
from werkzeug.utils import redirect

from bot.bot import Bot
from config import Config
from form import ProductForm
from search.search import Search

app = Flask(__name__)
app.config.from_object(Config)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['200 per day', '50 per hour', '1 per second']
    # default_limits=['1 per second']
)
socketio = SocketIO(app, cors_allowed_origins="*")

bot = Bot()


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


@socketio.on('search', namespace='/socket')
def search_product(product):
    import time
    emit('searching start')
    search = Search(product['data'])
    print(f'Searching for {search.search_term}')
    start_time = time.time()
    try:
        for shop in search.shops:
            if shop.json_selector is not None:
                try:
                    result = search.search_json(shop)
                except Exception as e:
                    error_message = f"SEARCH FAILED FOR SHOP [{shop.shop_name}] AND PRODUCT [{search.search_term}], REVERTING TO DEFAULT"
                    bot.send_message(error_message)
                    print(
                        f"SEARCH FAILED FOR SHOP [{shop.shop_name}] AND PRODUCT [{search.search_term}], REVERTING TO DEFAULT")
                    print(e)
                    page_source = search.load_page_source(shop)
                    result = search.search_page_source(page_source, shop)
            else:
                page_source = search.load_page_source(shop)
                result = search.search_page_source(page_source, shop)
            emit('result', {
                'shop_name': shop.shop_name,
                'result': result
            })
    except Exception as e:
        bot.send_message(repr(e))
    finally:
        print(f'Search for {search.search_term} took {time.time() - start_time}')
        emit('searching stop')


@socketio.on('connect', namespace='/socket')
def test_connect():
    emit('connection successful', {'data': 'Connected'})
    print('Client connected')
    socketio.sleep(0)


@socketio.on('disconnect', namespace='/socket')
def test_disconnect():
    print('Client disconnected')


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
