# -*- coding: utf-8 -*-

import os
import string
from flask import Flask, render_template, current_app, request
from app import FuzzyMatchingEngine

app = Flask(__name__)


# load configuration

if os.getenv('LES_CONFIG'):
    app.config.from_envvar('LES_CONFIG')
else:
    app.config.from_pyfile('app.cfg')

devel_mode = 'DEVELOPMENT_MODE' in app.config
share_sqlite = 'SHARE_SQLITE_CONN' in app.config


# all requests are done via the default route/URL by passing the query
# in the 'q' parameter

@app.route('/', methods=['GET', 'POST'])
def index():
    org_query = request.args.get('q')
    show_stats = request.args.get('stats')
    result = FuzzyMatchingEngine.SearchResult()

    if devel_mode:
        print("*** Query is: '%s'" % org_query)

    query = prepare_query(org_query)

    if query:
        engine = get_engine()
        result = engine.find_matches(query)
        result.org_query = org_query

    examples = [
        "чого вам не хвата, тюрми?",
        "А ти хуй в бєлки видів?",
        "Шо мовчите, скуштували хуя?"
    ]

    return render_template('results.html', result=result, examples=examples,
                           show_stats=show_stats, devel=devel_mode)


def prepare_query(query):
    """Clean up query string.

    We delete all punctuation and single-character words.
    """

    if not query:
        return None

    translator = get_translator()
    new_query = query.translate(translator).strip()
    new_query = ' '.join([w for w in new_query.split() if len(w) > 1])

    if (query != new_query) and devel_mode:
        print("*** Stripped query is: '%s'" % new_query)

    return new_query


def get_engine():
    "Build the engine object and load the data."

    if share_sqlite:
        engine = getattr(current_app, '_engine', None)

        if engine:
            return engine

    if devel_mode:
        print("*** Loading the search engine")

    engine = FuzzyMatchingEngine.FuzzyMatchingEngine()
    engine.open_db(app.config['DB_FILE'])
    engine.load_tokens()

    if share_sqlite:
        current_app._engine = engine

    return engine


def get_translator():
    "Build the character translator for punctuation removal."

    translator = getattr(current_app, '_translator', None)

    if translator is None:
        if devel_mode:
            print("*** Setting up the translator")

        translator = current_app._translator = \
            str.maketrans({key: None for key in string.punctuation})

    return translator


if __name__ == '__main__':
    app.run(debug=True)
