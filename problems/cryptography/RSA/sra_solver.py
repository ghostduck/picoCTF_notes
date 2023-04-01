#!/bin/env python3

from Crypto.Util.number import long_to_bytes
from string import ascii_letters, digits

POSSIBLE_CHARS = ascii_letters + digits  # type is str
PLAINTEXT_LENGTH = 16

# Helper method
def verify_n(de,n,c):
    if n < c:
        return False

    # de is de, not de-1 this case
    for i in range(2,100):
        if pow(i, de, n) != i:
            return False
    return True

def find_message(c,d,e=65537):
    # there are too many possible n for the same de
    # Therefore we need to print the correct plaintext message  according to the original script
    possible_n = recover_n(d,c,e)
    for (n,p,q) in possible_n:
        m = long_to_bytes(pow(c,d,n))

        if len(m) == PLAINTEXT_LENGTH and all(chr(c) in POSSIBLE_CHARS for c in m):
            print("n,p,q = {},{},{}".format(n,p,q))
            print(m)

def parse_factors():
    # originally the find_factors() function
    # now this is just to parse the output from website, factors of de-1
    factors = []

    # Copy output from https://www.alpertron.com.ar/ECM.HTM
    # Enter de-1 in the textbox. then press factor -> Press "Show divisors" -> Copy and paste every factors in factors.txt
    # It may have more than 1000 factors, if so press "Show more divisors" then keep copy and pasting

    with open("factors.txt") as f:
        for line in f:
            # Actually can use options to control the output format so we can skip parsing
            # The perfect option is: 0 digits per group, untick verbose mode and untick pretty print
            # Sample input for this line parse
            # 5823582 8278421659 2557489935 4572143890 7327043968 (47 digits)
            # 8914634736 1831653537 1390922124
            line = line.split(' (')[0]
            line = line.replace(' ', '')

            factor = int(line)
            if factor < (2**(8*PLAINTEXT_LENGTH+1))-1 : # 2^129 -1
                factors.append(factor)

    factors.sort()
    return factors

def find_n_from_factors(de,c,factors):
    possible_npq = []

    # Assume sorted
    for p in factors:
        for q in factors[::-1]:
            # double pointer search: p from start and q from end
            if p > q:
                break

            n = (p+1)*(q+1)
            #print(p+1, q+1)
            if n > c and verify_n(de, n, c):
                npq = (n, p+1, q+1)
                possible_npq.append(npq)

    return possible_npq

def recover_n(d,c,e=65537):
    de = d*e

    factors = parse_factors()
    # print(factors)

    # choose 2 among the factors - the correct pair would pass verify_n(de, n)
    # n must be greater than c - this is an extra hint
    #n,p,q = find_n_from_factors(de,c,factors)
    # print("n,p and q are {}, {}, {}".format(n,p,q))

    list_t_npq = find_n_from_factors(de,c,factors)
    #possible_n = [t[0] for t in list_t_npq]
    #return possible_n
    return list_t_npq


c = 1146568782252725017361183076550651612797135094478738648142497636283811770943
d = 22759416966030230998313989314135347766152611216178226844073651150263982112641
find_message(c,d)
