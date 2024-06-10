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

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filling_id INTEGER NOT NULL,
    asset TEXT,
    transaction_type TEXT,
    transaction_date TEXT,
    notification_date TEXT,
    amount TEXT,
    UNIQUE (filling_id, transaction_date, amount)
    FOREIGN KEY (filling_id) REFERENCES fillings(id)
);
