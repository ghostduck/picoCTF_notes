#

## Transformation

All we have is a encrypted byte file and this piece of code

```bash
$ file enc
enc: UTF-8 Unicode text, with no line terminators

# seems not really readable
$ cat enc
灩捯䍔䙻ㄶ形楴獟楮獴㌴摟潦弸彥ㄴㅡて㝽

$ xxd enc
00000000: e781 a9e6 8daf e48d 94e4 99bb e384 b6e5  ................
00000010: bda2 e6a5 b4e7 8d9f e6a5 aee7 8db4 e38c  ................
00000020: b4e6 919f e6bd a6e5 bcb8 e5bd a5e3 84b4  ................
00000030: e385 a1e3 81a6 e39d bd                   .........

```

```python
''.join([chr((ord(flag[i]) << 8) + ord(flag[i + 1])) for i in range(0, len(flag), 2)])

# Clearer formatting
[
    chr(
        (ord(flag[i]) << 8) + ord(flag[i + 1])
    )
    for i in range(0, len(flag), 2)
]

```

`ord()` is from letter to integer while chr() is from integer to letter.

That piece of code simply picks 2 ASCII letters, then packs them together as a 4 byte number, then print as a single character.

The script:

```python
# Reading it as raw byte -- but wrong way to this problem
with open('enc', 'rb') as f:
    enc_flag_bin = f.read()

print(flag)
b'\xe7\x81\xa9\xe6\x8d\xaf\xe4\x8d\x94\xe4\x99\xbb\xe3\x84\xb6\xe5\xbd\xa2\xe6\xa5\xb4\xe7\x8d\x9f\xe6\xa5\xae\xe7\x8d\xb4\xe3\x8c\xb4\xe6\x91\x9f\xe6\xbd\xa6\xe5\xbc\xb8\xe5\xbd\xa5\xe3\x84\xb4\xe3\x85\xa1\xe3\x81\xa6\xe3\x9d\xbd'

# Reading as normal text
with open('enc', 'r') as f:
    enc_flag_txt = f.read()

tmp_lst = []

for t in enc_flag_txt:
    num = ord(t)
    a1, a2 = num & 0x00ff, (num & 0xff00) >> 8
    tmp_lst.append(a1)
    tmp_lst.append(a2)

flag = ''.join([chr(i) for i in tmp_lst])
print(flag)
# ipocTC{F6...

# Endian problem ...
# So we have to change the order of a1 and a2

tmp_lst = []

for t in enc_flag_txt:
    num = ord(t)
    a2, a1 = num & 0x00ff, (num & 0xff00) >> 8  # only swapped a1 and a2 from above
    tmp_lst.append(a1)
    tmp_lst.append(a2)

correct_flag = ''.join([chr(i) for i in tmp_lst])
print(correct_flag)
```

## Thoughts

From the official documentation:

> ord(c)
>
> Given a string representing one Unicode character, return an integer representing the Unicode code point of that character.

So the "integer" we get from `ord()` is the code point. The code point can have different binary representation under different encoding schemes (namely UTF8, UTF16, UTF32)

Therefore we cannot directly work with the raw bytes.
