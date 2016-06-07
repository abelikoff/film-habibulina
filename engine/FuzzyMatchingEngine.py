#!/usr/bin/env python

import sqlite3
import operator
from functools import lru_cache


class FuzzyMatchingEngine:
    # Maximum allowed difference between two words
    MAX_WORD_DIFF_RATE = 0.5
    # Minimum allowed similarity score between two phrases
    MIN_SIMILARITY_SCORE = 0.65


    def __init__(self):
        self.all_tokens = {}
        self.db_conn = None


    def open_db(self, db_file):
        "Open quotes database."

        self.db_conn = sqlite3.connect(db_file, uri=True)


    def load_tokens(self):
        "Load quote tokens."

        c = self.db_conn.cursor()
        self.all_tokens = {}

        for row in c.execute('SELECT quote_id, tokens FROM quotes'):
            self.all_tokens[int(row[0])] = row[1].split()

        c.close()


    def find_matches(self, query):
        "Find matches for a given query phrase."

        words = query.lower().split()
        scores = {}

        for qid, tokens in self.all_tokens.items():
            s = self.__get_similarity_score(words, tokens)

            if s >= FuzzyMatchingEngine.MIN_SIMILARITY_SCORE:
                scores[qid] = s

        sorted_qids = sorted(scores.items(), key=operator.itemgetter(1),
                             reverse=True)
        results = []

        for t in sorted_qids[:4]:
            q = self.__get_quote(t[0])
            q['score'] = t[1]
            results.append(q)

        return results


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

                dist = self.__levenshtein(w1, w2)
                diff_rate = float(dist) / min(len(w1), len(w2))

                if diff_rate < FuzzyMatchingEngine.MAX_WORD_DIFF_RATE:
                    del unmatched1[w1]
                    del unmatched2[w2]

        return 1.0 / (1 + len(unmatched1) + len(unmatched2) * 0.01)


    @lru_cache(maxsize=1000000)
    def __levenshtein(self, s1, s2):
        "Levenshtein distance (from https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python)"

        if s1 == s2:
            return 0

        if len(s1) < len(s2):
            return self.__levenshtein(s2, s1)

        # len(s1) >= len(s2)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1       # than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


if __name__=='__main__':
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

    for query in queries:
        print("-" * 70)
        print("QUERY: " + query)
        print()
        matches = engine.find_matches(query)

        for m in matches:
            print("%s\n**%s**:  %s\n%.4f\n" % (m['play'], m['actor'],
                m['quote'], m['score']))
