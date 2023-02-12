#!/usr/bin/env python

# Run with Python 2

# revert AES-ABC
# Don't think there is a way to retrieve the key and plaintext
# Only can reverse the ABC back to ECB
# But that should give us an idea about how the image looks like (.ppm)

# In AES, each block has 16 bytes
# In this PPM image, each pixel has 3 byte


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
    # data is str in Python2 and bytes in Python3

    header = ""

    for i in range(3):
        header_i, data = remove_line(data)
        header += header_i

    return header, data

def revert_aes_abc(aes_abc_data):
    blocks = [aes_abc_data[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE] for i in range(len(aes_abc_data) / BLOCK_SIZE)]
    real_blocks = blocks[:]  # big trap 1: need to store the real bytes separately
    # don't forget blocks in AES-ABC are already
    iv = blocks[0]

    for i in range(len(blocks) - 1):
        prev_blk = int(blocks[i].encode('hex'), 16)
        curr_blk = int(blocks[i+1].encode('hex'), 16)

        # reversing this line
        # n_curr_blk = (prev_blk + curr_blk) % UMAX
        if prev_blk > curr_blk:
            # modded
            n_curr_blk = UMAX - prev_blk + curr_blk
        elif prev_blk < curr_blk:
            n_curr_blk = curr_blk - prev_blk
        else:
            # does not happen in question
            print("current block == previous block, current block could be 0 or UMAX")
            n_curr_blk = 0

        # blocks[i+1] = to_bytes(n_curr_blk)  # WRONG: big trap 1 - blocks[i+1] needs to be preserved for block[i+2]
        real_blocks[i+1] = to_bytes(n_curr_blk)  # big trap 1

    # trap 2: need to throw IV away - but this does not matter
    #ecb_data = "".join(real_blocks)
    ecb_data = "".join(real_blocks[1:])
    return iv, ecb_data


if __name__=="__main__":
    with open('body.enc.ppm', 'rb') as f:
        header, data = parse_header_ppm(f)
        # header is first 3 lines of file, not encrypted, meta data of PPM file
        # data is str in Python2 and bytes in Python3
        iv, aes_ecb_data = revert_aes_abc(data)

    with open('body.enc_ecb.ppm', 'wb') as fw:
        fw.write(header)  # header not changed
        fw.write(aes_ecb_data)  # Turn AES-ABC back to AES-ECB, which does not hide flag as an image
