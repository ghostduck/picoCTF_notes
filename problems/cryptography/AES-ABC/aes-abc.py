#!/usr/bin/env python

from Crypto.Cipher import AES
from key import KEY
import os
import math

BLOCK_SIZE = 16
UMAX = int(math.pow(256, BLOCK_SIZE))  # 256 ^ 16 == 2^128


def to_bytes(n):  # int to bytes, want to fit a 128 bit block
    s = hex(n)
    s_n = s[2:]  # skip "0x" as string
    if 'L' in s_n:
        s_n = s_n.replace('L', '') # remove L in the large number string
    if len(s_n) % 2 != 0:
        s_n = '0' + s_n
    decoded = s_n.decode('hex')  # cannot execute in Python3: str has no decode method, simply forcing byte to ASCII string (0x59 -> "Y", 0x00 -> "NUL byte")

    pad = (len(decoded) % BLOCK_SIZE)
    if pad != 0:
        decoded = "\0" * (BLOCK_SIZE - pad) + decoded
        #Just add 0s before the number, nothing like PKCS7
    return decoded


def remove_line(s):
    # returns the header line, and the rest of the file
    return s[:s.index('\n') + 1], s[s.index('\n')+1:]


def parse_header_ppm(f):
    data = f.read()

    header = ""

    for i in range(3):
        header_i, data = remove_line(data)
        header += header_i

    return header, data


def pad(pt):
    padding = BLOCK_SIZE - len(pt) % BLOCK_SIZE  # PKCS7 padding
    return pt + (chr(padding) * padding)

# Addition Block Chaining
def aes_abc_encrypt(pt):
    cipher = AES.new(KEY, AES.MODE_ECB)
    ct = cipher.encrypt(pad(pt))  # many ECB block with same key in ct

    blocks = [ct[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE] for i in range(len(ct) / BLOCK_SIZE)]
    iv = os.urandom(16)
    blocks.insert(0, iv)  # block[0] = IV

    # block[0] = 3
    # block[1] = 5 -> 5+3 -> 8
    # block[2] = 1 -> 1+8 -> 9

    for i in range(len(blocks) - 1):  # IV block not modified
        prev_blk = int(blocks[i].encode('hex'), 16)  # first time is IV (block[0]), next time it is modified block[1] [2]...
        curr_blk = int(blocks[i+1].encode('hex'), 16)

        n_curr_blk = (prev_blk + curr_blk) % UMAX
        # So for block[i] and block[i+1], if block[i] > block[i+1], it must be over the limit and reducded by modulus
        # if prev_blk == curr_blk, curr_blk can be 0 or UMAX ...
        blocks[i+1] = to_bytes(n_curr_blk)

    ct_abc = "".join(blocks)  # ct_abc is all the blocks as string, including the IV

    return iv, ct_abc, ct


if __name__=="__main__":
    with open('flag.ppm', 'rb') as f:
        header, data = parse_header_ppm(f)
        # header is first 3 lines of file, not encrypted, meta data of PPM file

    iv, c_img, ct = aes_abc_encrypt(data)
    # ct is thrown away, IV is first block in c_img
    # We can probably re-create ct with this "ABC" setup

    with open('body.enc.ppm', 'wb') as fw:
        fw.write(header)  # header not changed
        fw.write(c_img)  # We have the AES-ABC'ed image
