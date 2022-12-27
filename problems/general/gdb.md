# GDB

Try to copy and paste some commands I used to solve the basic GDB questions.

## GDB Test Drive

Basically just follow the instructions. Otherwise it will sleep for a long time before you can see the flag.

(Flow: Set breakpoint -> break at the line before long sleep -> skip the sleep -> see flag)

```bash
$ chmod +x gdbme
$ gdb gdbme
(gdb) layout asm
(gdb) break *(main+99)
(gdb) run
(gdb) jump *(main+104)

```

Try to use another way to solve this - reduce sleep time

```bash
# inside gdb
# Enable disassembler output
(gdb) set disassemble-next-line on
(gdb) show disassemble-next-line
Debugger's willingness to use disassemble-next-line is on.


(gdb) r

Breakpoint 3, 0x0000555555555325 in main ()
=> 0x0000555555555325 <main+94>:        bf a0 86 01 00  mov    $0x186a0,%edi
1: x/i $pc
=> 0x555555555325 <main+94>:    mov    $0x186a0,%edi

# --- Now it shows the instruction's value ---

# --- Doubt it sleeps for 0x186a0 seconds. ---
# --- So try to modify it to 1 secs only ---
=> 0x0000555555555325 <main+94>:        bf a0 86 01 00  mov    $0x186a0,%edi
1: x/i $pc
=> 0x555555555325 <main+94>:    mov    $0x186a0,%edi

# --- Modify the instructions painfully, byte by byte... Note that this is Little Endian so reverse the order ---
# We want 0x00 01 86 a0 -> 0x00 00 00 01
(gdb) set *(char*)0x0000555555555326 = 0x01
(gdb) set *(char*)0x0000555555555327 = 0x00
(gdb) set *(char*)0x0000555555555328 = 0x00
(gdb) x/i $pc # confirm the instruction modified
=> 0x555555555325 <main+94>:    mov    $0x1,%edi

# --- Seems good ---

# Try to do it as 32-bit integer
(gdb) set *(unsigned int*) 0x0000555555555326 = 0x01
(gdb) x/i $pc
=> 0x555555555325 <main+94>:    mov    $0x1,%edi

# --- Also work too ---
(gdb) cont
# --- shows the flag ---

```

## Some other commands

Copy and pasted / learnt from somewhere else

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
