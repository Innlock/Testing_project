DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id integer PRIMARY KEY,
    sender text,
    getter text,
    note text,
    good text,
    unit text,
    cost real,
    amount integer,
    issued integer,
    date_time text
);
