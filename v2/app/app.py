# -*- coding: utf-8 -*-


import FuzzyMatchingEngine
import os
import random
import string
import sys
from flask import Flask, render_template, current_app, request

sys.path.append("/var/www/html/govoritl.es/app")


app = Flask(__name__)


# load configuration

if os.getenv("LES_CONFIG"):
    app.config.from_envvar("LES_CONFIG")
else:
    app.config.from_pyfile("app.cfg")

devel_mode = "DEVELOPMENT_MODE" in app.config
share_sqlite = "SHARE_SQLITE_CONN" in app.config


# all requests are done via the default route/URL by passing the query
# in the 'q' parameter


@app.route("/", methods=["GET", "POST"])
def index():
    org_query = request.args.get("q")
    show_stats = request.args.get("stats")
    result = FuzzyMatchingEngine.SearchResult()

    if devel_mode:
        print("*** Query is: '%s'" % org_query)

    query = prepare_query(org_query)

    if query:
        engine = get_engine()
        result = engine.find_matches(query)
        result.org_query = org_query

    aux_data = get_aux_data()

    return render_template(
        "results.html",
        result=result,
        aux_data=aux_data,
        show_stats=show_stats,
        devel=devel_mode,
    )


@app.route("/<path:path>")
def static_proxy(path):
    "Allow serving any assets in the static directory."

    return app.send_static_file(path)


@app.errorhandler(404)
def page_not_found(e):
    "Show a 'not found' message."

    result = FuzzyMatchingEngine.SearchResult()
    result.org_query = ""
    result.status = "no matches"
    aux_data = get_aux_data()

    return (
        render_template(
            "results.html",
            result=result,
            aux_data=aux_data,
            show_stats=False,
            devel=devel_mode,
        ),
        404,
    )


def prepare_query(query):
    """Clean up query string.

        We delete all punctuation and single-character words.
    """

    if not query:
        return None

    translator = get_translator()
    new_query = query.translate(translator).strip()
    new_query = " ".join([w for w in new_query.split() if len(w) > 1])

    if (query != new_query) and devel_mode:
        print("*** Stripped query is: '%s'" % new_query)

    return new_query


def get_aux_data():
    """Build various auxilliary data.
    """

    aux_data = {"example_queries": [], "not_found_message": ""}

    examples = [
        "чого вам не хвата, тюрми?",
        "А ти хуй в бєлки видів?",
        "Шо мовчите, скуштували хуя?",
        "Йобане село!",
        "Так би усє кишки у тєбя і шваpкнули",
        "Я етого не люблю",
        "Дєтство Геббельса",
        "Молодой, культурний чєловєк бьйот кота",
    ]

    error_messages = [
        "сто чортів жабі в цицьку!",
        "сто гарпунів киту в сраку!",
        "сто п’яних кашалотів в твою мать!",
        "сто центнерів простіпоми тобі в сурло!",
        "сто чортів твоєму батькові!",
        "о найприємніший з приємних!",
    ]

    if not getattr(current_app, "_rng", None):
        random.seed()
        current_app._rng = True

    selected = random.sample(range(len(examples)), 3)

    for ii in selected:
        aux_data["example_queries"].append(examples[ii])

    n = random.randint(0, len(error_messages) - 1)
    aux_data["not_found_message"] = error_messages[n]
    return aux_data


def get_engine():
    "Build the engine object and load the data."

    if share_sqlite:
        engine = getattr(current_app, "_engine", None)

        if engine:
            return engine

    if devel_mode:
        print("*** Loading the search engine")

    engine = FuzzyMatchingEngine.FuzzyMatchingEngine()
    engine.open_db(app.config["DB_FILE"])
    engine.load_tokens()

    if share_sqlite:
        current_app._engine = engine

    return engine


def get_translator():
    "Build the character translator for punctuation removal."

    translator = getattr(current_app, "_translator", None)

    if not translator:
        if devel_mode:
            print("*** Setting up the translator")

        translator = current_app._translator = str.maketrans(
            {key: None for key in string.punctuation}
        )

    return translator


if __name__ == "__main__":
    app.run(debug=True)
