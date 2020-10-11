from flask import Flask, request, render_template, flash, session
from werkzeug.utils import redirect

from config import Config
from form import ProductForm
from search import Search

import json

app = Flask(__name__)
app.config.from_object(Config)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form['product'].strip() != '':
            session['search_term'] = request.form['product']
            search_result = Search(request.form['product'])
            search_result.search_all()
            session['result'] = search_result.to_json()
        return redirect('/')
    try:
        result = json.loads(session['result'])
        search_term = session['search_term']
    except KeyError:
        result = None
        search_term = None
    finally:
        remove_from_session('result')
        remove_from_session('search_term')
    form = ProductForm(product=search_term)
    return render_template('home.html', form=form, search_result=result)


def remove_from_session(key):
    try:
        session.pop(key)
    except KeyError:
        pass


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
