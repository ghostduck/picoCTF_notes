# One-time pad

One-time pad is unbreakable. Some of the questions are breakable since they violated some key principles.

## Easy Peasy

Not very difficult. Still we need to handle the output as hex string and setup the input to the server.

### Question

This is the running program.

```python
#!/usr/bin/python3 -u
import os.path

KEY_FILE = "key"
KEY_LEN = 50000
FLAG_FILE = "flag"

def startup(key_location):
    flag = open(FLAG_FILE).read()
    kf = open(KEY_FILE, "rb").read()

    start = key_location
    stop = key_location + len(flag)

    key = kf[start:stop]
    key_location = stop

    result = list(map(lambda p, k: "{:02x}".format(ord(p) ^ k), flag, key))
    print("This is the encrypted flag!\n{}\n".format("".join(result)))

    return key_location

def encrypt(key_location):
    ui = input("What data would you like to encrypt? ").rstrip()
    if len(ui) == 0 or len(ui) > KEY_LEN:
        return -1

    start = key_location
    stop = key_location + len(ui)

    kf = open(KEY_FILE, "rb").read()

    if stop >= KEY_LEN:
        stop = stop % KEY_LEN
        key = kf[start:] + kf[:stop]
    else:
        key = kf[start:stop]
        key_location = stop

    result = list(map(lambda p, k: "{:02x}".format(ord(p) ^ k), ui, key))

    print("Here ya go!\n{}\n".format("".join(result)))

    return key_location

print("******************Welcome to our OTP implementation!******************")
c = startup(0)
while c >= 0:
    c = encrypt(c)
```

And we are given the following output in the server:

```bash
******************Welcome to our OTP implementation!******************
This is the encrypted flag!
51124f4d194969633e4b52026f4c07513a6f4d05516e1e50536c4954066a1c57

What data would you like to encrypt?
```

We can input some strings after the prompt and it will use its OTP bytes to XOR with our strings (in hex as ASCII)

### Solution

The problem with the code is that it reuse the same OPT bytes after **KEY_LEN** of bytes. As long as we don't pass anything longer than KEY_LEN as input (to make it return -1), we can recover the bytes...

#### Setup for the input

```python
# The XOR'ed string in hex
s = '51124f4d194969633e4b52026f4c07513a6f4d05516e1e50536c4954066a1c57'

print(len(s))  # 64, means key has 32 bytes
print("".join([r'\x'+l+k for l,k in zip(s[0::2],s[1::2])]))  # This is the payload

# \x51\x12\x4f\x4d\x19\x49\x69\x63\x3e\x4b\x52\x02\x6f\x4c\x07\x51\x3a\x6f\x4d\x05\x51\x6e\x1e\x50\x53\x6c\x49\x54\x06\x6a\x1c\x57
```

The first 32 bytes in the program are used to XOR the key.

So we can consume 49968 bytes more, then the program will use the 32 bytes again...

```bash
python3 -c "print('\x00'*(50000-32)+'\n'+'\x51\x12\x4f\x4d\x19\x49\x69\x63\x3e\x4b\x52\x02\x6f\x4c\x07\x51\x3a\x6f\x4d\x05\x51\x6e\x1e\x50\x53\x6c\x49\x54\x06\x6a\x1c\x57'+'\n' )" > in.txt
```

So our input file (in.txt) will look like this:

```text
(invisible 49968 NUL bytes)+newline, which is the same as enter

(our payload 32 bytes)+newline
```

The payload 32 bytes are **OTP bytes XOR key bytes**. We want to XOR key bytes again such that **OPT bytes XOR key bytes XOR OPT bytes** which end up with the **key bytes** we wanted.

`$ cat in.txt | nc serverurl > out.txt`

Server output:

```text
******************Welcome to our OTP implementation!******************
This is the encrypted flag!
51124f4d194969633e4b52026f4c07513a6f4d05516e1e50536c4954066a1c57

What data would you like to encrypt? Here ya go!
(too long to be shown, the 49968 bytes we don't care about)

What data would you like to encrypt? Here ya go!
33356563623432336233623433343732...(flag output 32 bytes)
```

Finally, turn every 2 characters into 1 byte...

```python
# The XOR'ed string in hex
s = '333565636234323(flag output 32 bytes 64 character long hexstring)'

flag = "".join([chr(int(l+k,16)) for l,k in zip(s[0::2],s[1::2])])
print("picoCTF{{{0}}}".format(flag))
```
