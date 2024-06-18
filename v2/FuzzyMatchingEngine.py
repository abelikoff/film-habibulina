#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import editdistance
import sqlite3
import operator
import sys
from functools import lru_cache


class SearchResult:
    def __init__(self):
        self.org_query = ""               # original (unclean) query string
        self.query = ""                   # cleaned up query string
        self.status = "default"           # default, matches, no matches, error
        self.matches = []
        self.elapsed_time = None
        self.total_matches = 0
        self.error = None


class Match:
    def __init__(self):
        self.play_name = None
        self.actor = None
        self.quote = None
        self.url = None
        self.score = None
        self.quote_id = None


class FuzzyMatchingEngine:
    # Words with difference score less than this value are considered similar
    WORD_SIMILARITY_THRESHOLD = 0.35
    # Minimum similarity score for two phrases
    PHRASE_SIMILARITY_THRESHOLD = 0.65


    def __init__(self):
        self.all_tokens = {}
        self.db_conn = None
        self.last_error = None


    def open_db(self, db_file):
        "Open quotes database."

        try:
            self.db_conn = sqlite3.connect("file:%s?mode=ro" % db_file,
                                            uri=True)
        except Exception as ex:
            self.db_conn = None
            print("FIXME: DB open failed: " + str(ex))
            self.last_error = str(ex)


    def close_db(self):
        "Close database."

        if not self.db_conn:
            return

        self.db_conn.close()
        self.db_conn = None


    def load_tokens(self):
        "Load quote tokens."

        if not self.db_conn:
            return

        c = self.db_conn.cursor()
        self.all_tokens = {}

        for row in c.execute('SELECT quote_id, tokens FROM quotes'):
            self.all_tokens[int(row[0])] = row[1].split()

        c.close()


    def find_matches(self, query):
        "Find matches for a given query phrase."

        result = SearchResult()
        result.query = query

        if not self.db_conn:
            result.status = "error"
            result.error = "Database not open (" + self.last_error + ")"
            return result

        start_time = datetime.datetime.now()
        words = query.lower().split()
        scores = {}

        for qid, tokens in self.all_tokens.items():
            s = self.__get_similarity_score(words, tokens)

            if s >= FuzzyMatchingEngine.PHRASE_SIMILARITY_THRESHOLD:
                scores[qid] = s

        sorted_qids = sorted(scores.items(), key=operator.itemgetter(1),
                             reverse=True)
        result.total_matches = len(sorted_qids)
        result.status = "no matches"

        for t in sorted_qids[:4]:
            q = self.__get_quote(t[0])
            m = Match()
            m.play_name = q['play']
            m.actor = q['actor']
            m.quote = q['quote']
            m.url = q['url']
            m.quote_id, m.score = t
            result.matches.append(m)
            result.status = "matches"

        result.elapsed_time = (datetime.datetime.now() -
                               start_time).total_seconds()
        return result


    def __get_quote(self, quote_id):
        "Load full quote data by quote ID."

        query = """
        SELECT p.title, p.url, q.speaker, q.phrase FROM quotes q, plays p
        WHERE q.play_id = p.play_id AND q.quote_id = :ID;
        """
        c = self.db_conn.cursor()
        result = None

        for row in c.execute(query, { "ID" : quote_id }):
            result = dict(zip(['play', 'url', 'actor', 'quote'], row))

        c.close()
        return result


    def __get_similarity_score(self, query, phrase):
        """Calculate similarity score between query and phrase.

        Both arguments are arrays of normalized words.

        Score is between 0 and 1 (1 is near-perfect match).
        """

        unmatched1 = dict([ (x, True) for x in query ])
        unmatched2 = dict([ (x, True) for x in phrase ])

        for w1 in query:
            for w2 in phrase:
                if (not w1 in unmatched1) or (not w2 in unmatched2):
                    continue

                dist = editdistance.eval(w1, w2)
                diff_rate = float(dist) / max(len(w1), len(w2))

                if diff_rate < FuzzyMatchingEngine.WORD_SIMILARITY_THRESHOLD:
                    del unmatched1[w1]
                    del unmatched2[w2]

        return 1.0 / (1 + len(unmatched1) + len(unmatched2) * 0.001)


if __name__ == '__main__':
    engine = FuzzyMatchingEngine()
    engine.open_db("habib.db")
    engine.load_tokens()

    queries = [
        u"дослідники калу",
        u"Шо за ностальгія, чого вам щас не хвата, тюрми?",
        u"Така робота, шо нема шо спиздить",
        u"кишки шваpкнули",
        u"Шо мовчите, скуштували хуя"
    ]

    if len(sys.argv) > 1:
        queries = sys.argv[1:]

    for query in queries:
        result = engine.find_matches(query)
        print("=" * 70)
        print(query)
        print("=" * 70)
        print("%.3fs, %d matches\n" % (result.elapsed_time,
                                       result.total_matches))

        for m in result.matches:
            if m.actor:
                prefix = m.actor + ": "
            else:
                prefix = ""

            print("%s\n%s\n%s%s\n%d  %.4f\n" % (m.play_name,
                                            '-' * len(m.play_name),
                                            prefix,
                                            m.quote,
                                            m.quote_id,
                                            m.score))
