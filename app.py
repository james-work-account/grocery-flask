import json
import time
from datetime import timedelta
from distutils import util
from urllib.error import HTTPError

from flask import Flask, request, render_template, session, escape
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit
from werkzeug.utils import redirect

from bot.bot import Bot
from config import Config
from form import ProductForm
from helpers import clean_string
from search import search

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
if bot.user_id is not None:
    pass
else:
    bot = None

# setting up cache-on-a-budget
most_recent_cache = time.time()  # will be overridden when first request > max_cache_time is made
max_cache_time = 60 * 15  # 15 minutes
cache = dict()  # don't want to bother dealing with redis right now


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
def search_product(data):
    product = clean_string(data['product'])
    s = search.shops(product)
    emit('searching start', {
        'search_length': len(s)
    })
    print(f'Searching for {product}')
    start_time = time.time()

    # clear cache if request is more than max_cache_time since previous request
    global most_recent_cache
    global cache
    if start_time - most_recent_cache >= max_cache_time:
        most_recent_cache = start_time
        cache = dict()

    try:
        emit('search length', f'{len(s)}')
        search.max_length = int(escape(data['max_returned']))
        for i, shop in enumerate(s):
            try:
                # deal with cache - if key exists, assign value without bothering to re-search
                cache_key = f'{shop.shop_name}.{product}.{search.max_length}'
                cache_value = cache.get(cache_key)
                if cache_value is not None:
                    result = cache_value
                else:
                    if shop.json_selector is not None:
                        try:
                            result = search.search_json(shop)
                        except Exception as e:
                            error_message = f"SEARCH FAILED FOR SHOP [{shop.shop_name}] AND PRODUCT [{product}], REVERTING TO DEFAULT"
                            if not (isinstance(e, HTTPError) and shop.shop_name == "ALDI" and e.code == 503):
                                if bot is not None:
                                    bot.send_message(error_message, e)
                                print(
                                    f"SEARCH FAILED FOR SHOP [{shop.shop_name}] AND PRODUCT [{product}], REVERTING TO DEFAULT")
                                print(repr(e))
                            page_source = search.load_page_source(shop)
                            result = search.search_page_source(page_source, shop)
                    else:
                        page_source = search.load_page_source(shop)
                        result = search.search_page_source(page_source, shop)
                    # update cache with new value for shop/product/max combination
                    cache[cache_key] = result
                emit('result', {
                    'shop_name': shop.shop_name,
                    'result': result,
                    'shop_number': i + 1
                })
                socketio.sleep()  # Without this sleep, the app batches up the emits. I have no idea why. Maybe they're happening too quickly for it to keep up?
            except Exception as e:
                print(f'{product} - {shop.shop_name}', repr(e))
                if bot is not None:
                    bot.send_message_with_tag(f'{search_product} - {shop}', repr(e))
    except Exception as e:
        print(repr(e))
        if bot is not None:
            bot.send_message_with_tag('', repr(e))
    finally:
        print(f'Search for {product} took {time.time() - start_time}')
        emit('searching stop')


@socketio.on('connect', namespace='/socket')
def test_connect():
    emit('connection successful', {'data': 'Connected'})
    print('Client connected')
    socketio.sleep()


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
