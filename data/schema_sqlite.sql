-- schema for the quotes DB

CREATE TABLE plays (
       play_id INTEGER PRIMARY KEY AUTOINCREMENT,
       title VARCHAR(128) NOT NULL,
       url VARCHAR(512) NOT NULL
);

CREATE TABLE quotes (
       quote_id INTEGER PRIMARY KEY AUTOINCREMENT,
       play_id INTEGER NOT NULL,
       speaker VARCHAR(128),
       phrase TEXT NOT NULL,
       tokens TEXT NOT NULL	-- normalized and cleaned-up phrase
);
