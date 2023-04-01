# SRA

Now we need to find n from e and d. So we can solve the m from c.

## Question

Original source code:

```python
from Crypto.Util.number import getPrime, inverse, bytes_to_long
from string import ascii_letters, digits
from random import choice

pride = "".join(choice(ascii_letters + digits) for _ in range(16))  # ASCII string with length 16 - 128 bit
gluttony = getPrime(128)
greed = getPrime(128)
lust = gluttony * greed
sloth = 65537
envy = inverse(sloth, (gluttony - 1) * (greed - 1))

anger = pow(bytes_to_long(pride.encode()), sloth, lust)

print(f"{anger = }")
print(f"{envy = }")

print("vainglory?")
vainglory = input("> ").strip()

if vainglory == pride:
    print("Conquered!")
    with open("/challenge/flag.txt") as f:
        print(f.read())
else:
    print("Hubris!")

```

My modified source code:

```python
from Crypto.Util.number import getPrime, inverse, bytes_to_long
from string import ascii_letters, digits
from random import choice

random_str = "".join(choice(ascii_letters + digits) for _ in range(16))
p = getPrime(128)  # Note: 128 bits = 16 bytes, which is the same size with random_str
q = getPrime(128)
n = p * q
e = 65537
d = inverse(e, (p - 1) * (q - 1))

c = pow(bytes_to_long(random_str.encode()), e, n)  # encrypt random_str as big number

print(f"c = {c}") # anger
print(f"d = {d}") # envy

# So we have to find plaintext without n but d and e is known
# Or just try to find n from e and d
# We can verify n with c since we have e too
print("What is the random string??")
vainglory = input("> ").strip()

while True:
    if vainglory == random_str:
        print("Conquered!")
        print(random_str)
        break
        #with open("/challenge/flag.txt") as f:
        #    print(f.read())
    else:
        print("Hubris!")
        vainglory = input("> ").strip()  # retry
```

In brief, we have to find original plaintext message. To do this we need to find n in RSA (given we have d and e).

## More details

Need to implement a function to recover n from e and d.

p and q are quite small (128 bits, still too big to brute force) but seems there are no easy formula to find n...

```python
from Crypto.Util.number import long_to_bytes

# Helper method
def verify_n(de,n):
    for i in range(2,100):
        if pow(i, de, n) != i:
            return False
    return True

def find_message(c,d,e=65537):
    n = recover_n(d,e)
    m = long_to_bytes(pow(c,d,n))
    return m

def recover_n(d,e=65537):
    # implement it
    return n

print(find_message(c,d))
```

## Maths time

Basic setup (p,q and e) are listed in the RSA code above, so I don't mention them again.

The trick to make RSA works are...

```txt
Euler's Theorem - Let n be a positive integer, and let a be an integer that is relatively prime to n.

 ϕ(n)
a     ≡ 1 (mod n)

---------------------
RSA

 de
m  ≡ m (mod n)

So de is kϕ(n)+1 from Euler's Theorem

 de-1
m    ≡ 1 (mod n)

And we know de forms at least one cycle (under mod n)
(The exact power forming a cycle is LCM(p-1, q-1), which is known as Carmichael function)

-------------------------
Correctness of RSA

                          k
 kϕ(n)+1    kϕ(n)     ϕ(n)        k
m        ≡ m     ⋅m ≡ m     ⋅m ≡ 1 ⋅m ≡ m (mod n)

------------------------
de ≡ 1 (mod ϕ(n))

So de can be written as ...

de = kϕ(n) + 1
de-1 = kϕ(n)

(de-1) is multiple of ϕ(n). In other words, ϕ(n) is a factor of (de-1)
------------------------
 ϕ(n)
a     ≡ 1 (mod n)

 (p-1)(q-1)
a           ≡ 1 (mod pq)

de-1 = k⋅(p-1)⋅(q-1)
= k (pq-p-q+1)

What can I do if I know ϕ(n)?

```

## Actual findings on the problem

By running a smaller example, I found something ...

```text
Sample input

# real question
# Set 1
c = 1146568782252725017361183076550651612797135094478738648142497636283811770943
d,e = 22759416966030230998313989314135347766152611216178226844073651150263982112641, 65537
# very large number

# Set 2
p=614477
q=699539
n=429850626103
random string is: fe (26213, 0x6665)
c = 20583746836
d = 114170422441
e = 65537


# Set 3
p,q = 479,521
n = 249559
phi_n = 248560 # (p-1)(q-1)

# LCM(478,520) = 124280 (HCF==2)

c = 4576 (random string is 'I7', which is 18743, 0x4937)
e = 3, d = 165707
de = 497121
# de mod lcm ≡ 1
# de mod phi_n ≡ 1 too

# h(p-1)(q-1) = de-1, where h=2 for this case
# phi_n, (p-1) and (q-1) are all inside...
# All factors of de-1 (497120): 1, 2, 4, 5, 8, 10, 13, 16, 20, 26, 32, 40, 52, 65, 80, 104, 130, 160, 208, 239, 260, 416, 478, 520, 956, 1040, 1195, 1912, 2080, 2390, 3107, 3824, 4780, 6214, 7648, 9560, 12428, 15535, 19120, 24856, 31070, 38240, 49712, 62140, 99424, 124280, 248560, 497120

# Pair-up
# One of the pairs contains phi_n and HCF(h), so we can find LCM(p,q) from the pair
# (1,497120), (2,248560), (4,124280), (5,99424), (8,62140), (10, 49712), (13,38240), (16, 31070), (20, 24856), (26,19120), (32, 15535), (40, 12428), (52, 9560), (65, 7648), (80, 6214), (104,4780), (130,3824), (160,3107), (208,2390), (239,2080), (260,1912), (416,1195), (478,1040), (520, 956)

# The principle: after +1, if that number is not a prime, we don't want it

# The numbers in the challenge will be too big to factor

# Remember de forms at least 1 cycle
# So we don't really need to bother to find the LCM, phi_n is good enough for this question

# de - 1 = k * lcm

# ... still, how can we find n from e and d?
# Try c = 4576 (random string is 'I7', which is 18743, 0x4937)
#     d
# 4576  mod (de-1) = 403936
```

## Another larger example

```python

# p=614477
# q=699539
# n=429850626103
# random string is: fe (26213, 0x6665)

# phi_n = 429849312088

PLAINTEXT_LENGTH = 2
c = 20583746836
d = 114170422441
find_message(c,d) # e=65537

# de = 7482386975515817
# de -1 // phi_n == 17407
```

"Prime" factors only:
[1, 2, 4, 28, 52, 58, 232, 676, 1192, 2062, 2086, 4732, 5278, 9802, 15496, 37492, 39208, 50362, 57736, 89596, 122776, 201448, 274456, 399022, 487396, 614476, 699538, 859432, 1164748, 1299142, 1393912, 1780252, 2761018, 6674902, 8153236, 8909902, 9228388, 10293202, 10883236, 16888846, 19327126, 23143276, 24869782, 28268968, 35639608, 41172808, 63291028, 86773726, 99479128, 118221922, 133811626, 143572936, 162002932, 184746952, 211543048, 249477256, 300862588, 443037196, 472887688, 607416082, 687514906, 726925108, 1120973308, 1739551138, 2561587546, 3067374196, 4812604342, 6023093752, 6424039342, 7411195036, 11930358778, 12176857966, 15351761146, 18751815628, 35750775112, 62563856446, 107462328022, 133202552392, 178927423012, 763353088708, 1417655736172, 1581231398038, 1731633181096, 3586954446556, 3628703673868, 10377790534696, 25108681125892, 72644533742872, 82224032697976, 267228106268422, 575568228885832]

All factors:
[1, 2, 4, 7, 8, 13, 14, 26, 28, 29, 52, 56, 58, 91, 103, 104, 116, 149, 169, 182, 203, 206, 232, 298, 338, 364, 377, 406, 412, 596, 676, 721, 728, 754, 812, 824, 1031, 1043, 1183, 1192, 1339, 1352, 1442, 1508, 1624, 1723, 1937, 2062, 2086, 2366, 2639, 2678, 2884, 2987, 3016, 3446, 3874, 4124, 4172, 4321, 4732, 4901, 5278, 5356, 5768, 5974, 6892, 7217, 7748, 8248, 8344, 8642, 9373, 9464, 9802, 10556, 10712, 11948, 12061, 13403, 13559, 13784, 14434, 15347, 15496, 17284, 17407, 18746, 19604, 20909, 21112, 22399, 23896, 24122, 25181, 26806, 27118, 28868, 29899, 30247, 30694, 34307, 34568, 34814, 37492, 38831, 39208, 41818, 44798, 48244, 49967, 50362, 53612, 54236, 56173, 57736, 59798, 60494, 61388, 68614, 69628, 74984, 77662, 83636, 89596, 93821, 96488, 99934, 100724, 106193, 107224, 107429, 108472, 112346, 119596, 120988, 121849, 122776, 137228, 139256, 153619, 155324, 156793, 167272, 174239, 176267, 177469, 179192, 187642, 199511, 199868, 201448, 209293, 212386, 214858, 224692, 239192, 241976, 243698, 256727, 271817, 274456, 291187, 307238, 310648, 313586, 348478, 349769, 352534, 354938, 375284, 388687, 393211, 399022, 399736, 418586, 424772, 429716, 445063, 449384, 487396, 504803, 513454, 543634, 582374, 614476, 627172, 649571, 696956, 699538, 705068, 709876, 730249, 743351, 750568, 777374, 786422, 798044, 837172, 849544, 859432, 890126, 974792, 1009606, 1026908, 1075333, 1087268, 1164748, 1219673, 1228952, 1242283, 1254344, 1299142, 1380509, 1393912, 1396577, 1399076, 1410136, 1419752, 1460498, 1486702, 1554748, 1572844, 1596088, 1674344, 1776413, 1780252, 1797089, 1997047, 2019212, 2038309, 2053816, 2150666, 2174536, 2307097, 2329496, 2439346, 2484566, 2593643, 2598284, 2720809, 2761018, 2793154, 2798152, 2920996, 2973404, 3079597, 3109496, 3115441, 3145688, 3337451, 3533621, 3552826, 3560504, 3594178, 3994094, 4038424, 4076618, 4301332, 4454951, 4546997, 4614194, 4878692, 4969132, 5052931, 5111743, 5146601, 5187286, 5196568, 5441618, 5522036, 5586308, 5785819, 5841992, 5946808, 6159194, 6230882, 6674902, 7067242, 7105652, 7188356, 7445083, 7988188, 8153236, 8444423, 8602664, 8909902, 9093994, 9228388, 9663563, 9757384, 9938264, 10105862, 10223486, 10293202, 10374572, 10883236, 11044072, 11172616, 11571638, 12318388, 12434891, 12461764, 13349804, 13979329, 14134484, 14211304, 14376712, 14890166, 15822757, 15976376, 16149679, 16306472, 16888846, 17819804, 17946617, 18155501, 18187988, 18456776, 19327126, 20211724, 20446972, 20586404, 20749144, 21557179, 21766472, 23093369, 23143276, 23362157, 24636776, 24869782, 24923528, 25961611, 26442881, 26699608, 27958658, 28268968, 29780332, 29992261, 31184657, 31645514, 32299358, 33777692, 35370517, 35639608, 35893234, 36026207, 36311002, 36375976, 38654252, 40034761, 40423448, 40500733, 40893944, 41172808, 43114358, 43386863, 46186738, 46286552, 46724314, 49739564, 51515977, 51923222, 52115581, 52885762, 55917316, 57914363, 59110961, 59560664, 59984522, 62369314, 63291028, 64598716, 66905813, 67555384, 70741034, 71786468, 72052414, 72622004, 75215647, 77308504, 80069522, 81001466, 86228716, 86773726, 92373476, 93448628, 96786079, 99479128, 103031954, 103846444, 104231162, 105771524, 110759299, 111834632, 115828726, 118221922, 119969044, 124738628, 125626319, 126582056, 129197432, 133811626, 141482068, 143572936, 144104828, 145244008, 150431294, 160139044, 161653583, 162002932, 172457432, 173547452, 181731277, 182970539, 184746952, 185100167, 186897256, 193572158, 205695841, 206063908, 207692888, 208462324, 209945827, 211543048, 221518598, 231657452, 236443844, 239938088, 249477256, 251252638, 264685537, 267623252, 280243327, 282964136, 288209656, 300213797, 300862588, 303708041, 320278088, 323307166, 324005864, 343757453, 347094904, 360611839, 363462554, 365941078, 370200334, 387144316, 405400541, 411391682, 412127816, 416924648, 419891654, 443037196, 458859953, 463314904, 468340691, 472887688, 502505276, 520451893, 526509529, 529371074, 535246504, 560486654, 600427594, 601725176, 607416082, 646614332, 669707701, 677502553, 687514906, 721223678, 726925108, 731882156, 740400668, 752886719, 766843549, 774288632, 810801082, 822783364, 839783308, 869775569, 886074392, 917719906, 936681382, 1005010552, 1040903786, 1053019058, 1058742148, 1120973308, 1200855188, 1214832164, 1258219027, 1280793773, 1293228664, 1339415402, 1355005106, 1375029812, 1439870887, 1442447356, 1453850216, 1463764312, 1480801336, 1505773438, 1533687098, 1621602164, 1645566728, 1679566616, 1739551138, 1835439812, 1852798759, 1873362764, 2081807572, 2101496579, 2106038116, 2117484296, 2241946616, 2378617007, 2401710376, 2406302171, 2429664328, 2516438054, 2561587546, 2674045933, 2678830804, 2710010212, 2750059624, 2879741774, 2884894712, 3011546876, 3067374196, 3212019671, 3243204328, 3440911981, 3479102276, 3643163251, 3670879624, 3705597518, 3746725528, 4163615144, 4202993158, 4212076232, 4468846889, 4687953907, 4757234014, 4812604342, 5032876108, 5123175092, 5270207033, 5306145631, 5348091866, 5357661608, 5367904843, 5420020424, 5759483548, 5965179389, 6023093752, 6088428983, 6134748392, 6424039342, 6881823962, 6958204552, 7286326502, 7411195036, 7675880573, 8405986316, 8706200113, 8807533189, 8937693778, 9375907814, 9514468028, 9625208684, 9968966137, 10065752216, 10246350184, 10540414066, 10612291262, 10696183732, 10735809686, 11518967096, 11930358778, 12176857966, 12848078684, 13763647924, 14572653004, 14822390072, 15351761146, 16650319049, 16811972632, 17412400226, 17615066378, 17875387556, 18718321531, 18751815628, 19028936056, 19250417368, 19937932274, 21080828132, 21224582524, 21392367464, 21471619372, 23860717556, 24086383867, 24353715932, 25696157368, 27262610311, 27527295848, 29145306008, 30703522292, 30922021091, 31281928223, 33300638098, 34824800452, 35230132756, 35750775112, 37143019417, 37436643062, 37503631256, 39875864548, 41756255723, 42161656264, 42449165048, 42943238744, 44731855753, 47721435112, 48172767734, 48707431864, 53731164011, 54525220622, 60943400791, 61407044584, 61844042182, 62563856446, 66601276196, 68979893203, 69649600904, 69782762959, 70460265512, 74286038834, 74873286124, 77547332057, 79751729096, 83512511446, 89463711506, 96345535468, 99786447449, 107462328022, 109050441244, 121886801582, 123688084364, 125127712892, 129596559781, 133202552392, 137959786406, 139565525918, 148572077668, 149746572248, 155094664114, 167025022892, 178927423012, 190838272177, 192691070936, 199572894898, 214924656044, 216454147637, 218100882488, 243773603164, 247376168728, 250255425784, 259193119562, 275919572812, 279131051836, 297144155336, 310189328228, 313122990271, 334050045784, 354413934043, 357854846024, 381676544354, 399145789796, 429849312088, 432908295274, 482859252421, 487547206328, 518386239124, 542831324399, 551839145624, 558262103672, 620378656456, 626245980542, 698505132143, 708827868086, 763353088708, 790615699019, 798291579592, 865816590548, 896738611639, 907175918467, 965718504842, 1036772478248, 1085662648798, 1252491961084, 1297223816837, 1397010264286, 1417655736172, 1526706177416, 1581231398038, 1731633181096, 1793477223278, 1814351836934, 1931437009684, 2171325297596, 2480897538301, 2504983922168, 2594447633674, 2794020528572, 2835311472344, 3162462796076, 3586954446556, 3628703673868, 3862874019368, 4342650595192, 4607381142559, 4961795076602, 5188895267348, 5534309893133, 5588041057144, 6277170281473, 6324925592152, 7173908893112, 7257407347736, 9080566717859, 9214762285118, 9923590153204, 10278004087247, 10377790534696, 11068619786266, 12554340562946, 18161133435718, 18429524570236, 19847180306408, 20556008174494, 22137239572532, 25108681125892, 32251667997913, 36322266871436, 36859049140472, 41112016348988, 44274479145064, 50217362251784, 64503335995826, 71946028610729, 72644533742872, 82224032697976, 129006671991652, 133614053134211, 143892057221458, 258013343983304, 267228106268422, 287784114442916, 534456212536844, 575568228885832, 935298371939477, 1068912425073688, 1870596743878954, 3741193487757908, 7482386975515816]

Output from program:
n,p,q = 429850626103,614477,699539

## Intermediate solving script

The idea works but just too slow to run...

It takes ~1 minute to solve a 53-bit de-1 (20-bit p and q). It is hopeless to solve 256-bit de-1.

```python
#!/bin/env python3

from Crypto.Util.number import long_to_bytes
from string import ascii_letters, digits

lst_of_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

POSSIBLE_CHARS = ascii_letters + digits  # type is str
PLAINTEXT_LENGTH = 16

# Helper method
def verify_n(de,n,c):
    if n < c:
        return False

    # de is de, not de-1 this case
    for i in range(2,1000):
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

# --------------------------#

# Accuracy depends on size of k and lst_of_primes
def check_known_composite(k):
    if k in lst_of_primes:
        return False
    else:
        for p in lst_of_primes:
            if k % p == 0:
                return True

    return False

# Not really prime factors since we only prevent composites with factors from 1 to 1000
# And the factors inside are (p-1) and (q-1)
def find_factors(de_1):
    # de_1 is actually de -1
    factors = []

    a=1

    while a**2 <= de_1:
        if de_1 % a == 0:
            b = de_1//a

            if not check_known_composite(a+1):
                factors.append(a)
            if not check_known_composite(b+1) and b != a:
                factors.append(b)
        a+=1

    factors.sort()
    return factors

def find_n_from_factors(de,c,factors):
    possible_npq = []

    # Assume sorted
    for p in factors:
        for q in factors[::-1]: # search q from backward, some tricks try to reduce unwanted multiplication
            n = (p+1)*(q+1)
            if p > q:
                break
            if n > c and verify_n(de, n, c):
                npq = (n, p+1, q+1)
                possible_npq.append(npq)

    return possible_npq

def recover_n(d,c,e=65537):
    de = d*e

    factors = find_factors(de-1)
    # print(factors)

    # choose 2 among the factors - the correct pair would pass verify_n(de, n)
    # n must be greater than c - this is an extra hint
    #n,p,q = find_n_from_factors(de,c,factors)
    # print("n,p and q are {}, {}, {}".format(n,p,q))

    list_t_npq = find_n_from_factors(de,c,factors)
    #possible_n = [t[0] for t in list_t_npq]
    #return possible_n
    return list_t_npq

# --------------------------

# Set 0 - very small example, but bad example actually, several message with different n but same de are possible
# p,q = 479,521
# n = 249559

# c = 4576 # (random string is 'I7', which is 18743, 0x4937)
# d = 165707
# e = 3

#c = 4576
#d = 165707
#find_message(c,d,3)

# -----------------

# Set 1 - real question (Takes too long to run)
#c = 1146568782252725017361183076550651612797135094478738648142497636283811770943
#d = 22759416966030230998313989314135347766152611216178226844073651150263982112641

# -----------------

# Set 2 - smaller (This 16-bit example would take 1 minute...)
# p=614477
# q=699539
# n=429850626103
# random string is: fe (26213, 0x6665)
PLAINTEXT_LENGTH = 2
c = 20583746836
d = 114170422441
find_message(c,d)

# de.bit_length() == 53
# p=614477
# q=699539
# phi_n = (p-1)*(q-1)
# phi_n.bit_length() == 39
```

## Final solution

Trial division locally is too slow to do 256-bit de. So try to use some other fast factorization methods (sub-contracting the hard part!)...

For the code, check `sra_solver.py`.

<https://www.alpertron.com.ar/ECM.HTM> This is the fast factorization. Then all I need to do is to parse its output in `factors.txt`.

```bash
# c = 1146568782252725017361183076550651612797135094478738648142497636283811770943
# d = 22759416966030230998313989314135347766152611216178226844073651150263982112641
$ python3 sra_solver.py # with current commited factors.txt

n,p,q = 62983865792700078073494802705873164705777936407126448268102762873718498130113,245710990866211090142112277350324110729,256333123604530198818058102708407288697
b'MxlxXuHEe6MqFqyp'
```

## Extra information

The modfied simplier question script for testing

```python
#!/bin/env python3
from Crypto.Util.number import getPrime, inverse, bytes_to_long
from string import ascii_letters, digits
from random import choice

# helper for testing only
def GCD(a,b):
    if b>a:
        a,b = b,a
    while b != 0:
        a,b = b, a%b
    return a

STR_LENGTH = 16
random_str = "".join(choice(ascii_letters + digits) for _ in range(STR_LENGTH))
p = getPrime(STR_LENGTH * 8)
q = getPrime(STR_LENGTH * 8)
n = p * q
e = 65537  # can change to 3
d = inverse(e, (p - 1) * (q - 1))

big_num_m = bytes_to_long(random_str.encode())
c = pow(big_num_m, e, n)

print("--Testing version--")
print("p={},q={}".format(p,q))
print("n={}".format(n))

print("ϕ(n)is {}".format((p-1)*(q-1)))
print("de is {}".format(d*e))
print("inflated constant of (de-1) (h) is {}".format( ((d*e)-1) // ((p-1)*(q-1)) ))
# h can be less than 1xxx ~ 6xxxx for 128 bit primes... within range of 2**STR_LENGTH?

c_lcm = ((p-1)*(q-1)) // GCD(p-1, q-1)
print("Carmichael LCM = {}".format(c_lcm))
print("inflated constant of (de-1) compare to LCM is {}".format(((d*e)-1) // c_lcm))
# smallest number can be double of h to 24x h, have seen double many times

print("random string is: {}".format(random_str))
print("Plaintext message as number is: {}".format(big_num_m))

print(f"c = {c}")
print(f"d = {d}")

print("What is the random string??")
vainglory = input("> ").strip()

while True:
    if vainglory == random_str:
        print("Conquered!")
        print(random_str)
        break
        #with open("/challenge/flag.txt") as f:
        #    print(f.read())
    else:
        print("Hubris!")
        vainglory = input("> ").strip()  # retry
```
