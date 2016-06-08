from flask import Flask, render_template
from app import FuzzyMatchingEngine

app = Flask(__name__)


@app.route('/')
def index():
    #current_app['foo'] = "jkdhgkjdd"

    engine = FuzzyMatchingEngine.FuzzyMatchingEngine()
    engine.open_db("./app/habib.db")
    engine.load_tokens()
    query = u"дослідники калу"
    matches = engine.find_matches(query)

    for m in matches:
        print("%s\n**%s**:  %s\n%.4f\n" % (m['play'], m['actor'],
                                           m['quote'], m['score']))


    return render_template('default.html')


@app.route('/<query>')
def run_query(query):
    #current_app['foo'] = "jkdhgkjdd"

    engine = FuzzyMatchingEngine.FuzzyMatchingEngine()
    engine.open_db("./app/habib.db")
    engine.load_tokens()
    #query = u"дослідники калу"
    result = engine.find_matches(query)

    print("%.3fs\n" % result.elapsed_time)

    for m in result.matches:
        print("%s\n**%s**:  %s\n%.4f\n" % (m.play_name, m.actor,
                                           m.quote, m.score))

    return render_template('results.html', query=query, result=result, devel=True)


if __name__ == '__main__':
    app.run(debug=True)
