# General Notes

- Use `cat` or `less` to read plaintext
- You may need to download and run programs from PicoCTF (hopefully no virus)

```bash
wget link_to_that_executable
chmod +x that_executable
./that_executable
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

- picoCTF is generous to open some servers/containers for us to play around with, connect to them using `ncat`

```bash
nc mercury.picoctf.net 22342
```

- If I want to use some Python libraries to help to reduce manual works:

```bash
# setup venv
python3 -m venv env/picoCTF

# activate it
source env/picoCTF/bin/activate

# get the pwn module
pip install --upgrade pip
python3 -m pip install wheel
python3 -m pip install --upgrade pwntools
```

- If I want to leave the virtual environment without ending terminal session

```bash
deactivate
```
