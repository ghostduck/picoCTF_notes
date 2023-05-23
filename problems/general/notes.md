# General Notes

- Use `cat` or `less` to read plaintext
- You may need to download and run programs from PicoCTF (hopefully no virus)

```bash
wget link_to_that_executable
chmod +x that_executable
./that_executable
```

- Display a Base64 string (if it can be shown as normal text):

```bash
echo "that base64 string" | base64 --decode

# Or use Python
echo  "some base64 string" | python3 -m base64 -d
```

- Find a file using `find`

```bash
# There are many properties that can be used with find
find files/ -name uber-secret.txt
```

- Watch out for extra newline character when passing strings via echo: (From question HashingJobApp)

```bash
$ echo -n "gachiBASS"  | md5sum  # This is parsing really just "gachiBASS"
21b1f2a39d204ea9ad743d6aff8c09c5  -
$ echo "gachiBASS" | md5sum   # This is parsing "gachiBASS\n", probably not what we want
cdea510f0c0bf87a7bd3ea7657162b41  -
```

- Flag format is like `picoCTF{something_longer_andmore}`
- The ASCII in number for "picoCTF{_}": 112 105 99 111 67 84 70 123 95 125

```python
s = "picoCTF{_}"
for c in s:
    print(ord(c), end=" ")
print()

```

- In Hex (not writing 0x): 70 69 63 6f 43 54 46 7b 5f 7d

- The above is for Big endian. When it is Little endian, the pattern for `pico` will be 6f 63 69 70

- If you have a byte plaintext file like `706963...` which is like the flag, you cat just pipe it to `xxd -r -p` to show its ASCII content.

```bash
$ cat flag.txt
7069636f43

$ cat flag.txt | xxd -r -p
picoC
```

- picoCTF is generous to open some servers/containers for us to play around with, connect to them using `ncat`

```bash
nc mercury.picoctf.net 22342
```

The output can be piped. From the question ["plumbing"](https://play.picoctf.org/practice/challenge/48?category=5&page=3)

```bash
nc jupiter.challenges.picoctf.org 14291 | grep "picoCTF{"
```

- For shells without `cat` and `ls` (picoCTF 2023 Specialer)

Reference: <https://jarv.org/posts/cat-without-cat/>

We can still use Tabs to check for files/directories, or `echo *` to show file names (as `ls`).

Use `echo "$(<file.txt)"` as `cat file.txt`. Note that without the quotes(`""`) all newlines in the file will disappear.

> Explanation of this syntax: This syntax $(<file.txt) may look a bit strange, what you are doing is command substitution, where the contents of file.txt are sent to STDIN which is then echo’d as STDOUT.

These can be useful in some very lightweight container environments.

- If I want to use some Python libraries to help to reduce manual works:

```bash
# setup venv
python3 -m venv env/picoCTF

# activate it
source env/picoCTF/bin/activate

# get the pwn module
pip install --upgrade pip  # Seems python3 -m pip install --upgrade pip # is ok too
python3 -m pip install wheel
python3 -m pip install --upgrade pwntools
```

- If I want to leave the virtual environment without ending terminal session

```bash
deactivate
```
