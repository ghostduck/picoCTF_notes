# pw cracking (Python code reading check + simple editing)

I give these question the name of `Python code reading check + simple editing` as this is what the question is about.

I have done 1-4 without much problem so we skip to 5 directly...

## Problem

<https://play.picoctf.org/practice/challenge/249?category=5&page=3>

(Read and edit and) Run the Python code to find the correct MD5 hash of a hex-string so that we can find which one matches the wanted-hash and get the flag.

The problem is not that difficult as you can edit the code to input the `user_password` for you...

## Solution

Edit the code then brute force.

Check the content of dictionary, it is from 0 to 65535 in hex (lowercase)

```text
0000
0001
0002
...
000a
000b
...
fffe
ffff
```

The original Python code

```python
def level_5_pw_check():
    user_pw = input("Please enter correct password for flag: ")
    user_pw_hash = hash_pw(user_pw)

    # Note: correct_pw_hash is 16 bytes from file
    # We need to supply the string to generate the hash for user_pw_hash
    if( user_pw_hash == correct_pw_hash ):
        print("Welcome back... your flag, user:")
        decryption = str_xor(flag_enc.decode(), user_pw)
        print(decryption)
        return
    print("That password is incorrect")

level_5_pw_check()
```

No way I am going to enter them myself. So I change the code and try every password string in a simple for loop...

```python
def level_5_pw_check(user_pw):
    #user_pw = input("Please enter correct password for flag: ")
    user_pw_hash = hash_pw(user_pw)

    if( user_pw_hash == correct_pw_hash ):
        print("Newly added: correct pw is {}".format(user_pw))
        print("Welcome back... your flag, user:")
        decryption = str_xor(flag_enc.decode(), user_pw)
        print(decryption)
        return True
    # print("That password is incorrect")

# level_5_pw_check()

for i in range(0xffff + 1):
    i_in_str = '{:04x}'.format(i)  # lowercase, minimum length of 4
    if level_5_pw_check(i_in_str):  # end earlier if found password
        break
```

~~I spend most of my time searching how to format the string and write this~~
