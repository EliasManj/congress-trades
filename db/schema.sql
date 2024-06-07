CREATE TABLE persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prefix TEXT,
    lastname TEXT,
    firstname TEXT,
    suffix TEXT,
    UNIQUE (prefix, lastname, firstname)
);

CREATE TABLE fillings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    filing_type TEXT,
    state_dst TEXT,
    year TEXT,
    filing_date TEXT,
    docid TEXT,
    UNIQUE (person_id, filing_date, docid)
    FOREIGN KEY (person_id) REFERENCES persons(id)
);