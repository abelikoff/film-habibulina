# -*- coding: utf-8 -*-

import sqlite3

class QuoteFinder:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.crs = self.conn.cursor()

    def find(self, query):
        for row in self.crs.execute('SELECT * FROM quotes'):
            print row


if __name__=='__main__':
    engine = QuoteFinder('../data/habib.db')
    engine.find(u"кишки шваpкнули")
