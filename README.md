# My notes and writeups of picoCTF

As title. I put my notes and writeups of picoCTF in this repo.

The questions are categorized into 6 different types.

## General

They are not supposed to be very difficult.

Some questions can be solved by a search and they ask about different type of things including shell, setting up the environment (`nc`, `ssh`), straightforward Linux commands, quite simple Python codes, basic binary number system, encoding ... just can be anything.

## Forensics

At the moment I write this I still haven't solved many problems in the Forensics category.

This is like a more advanced and deeper general category. It includes question about things behind the scene (PEM file fields,), Wireshark log, file types, file header, file recovery and Steganography...

It seems we need to use the correct tools for each different thing.

## Cryptography

This category is self-descriptive. Public key and symmetric key encryption. Hash as well.

## Web Exploitation

Another self-descriptive category. Most of them can be done with a web browser/cURL.

Includes some questions about pure Javascript (no server) and some server processing your requests (so you have to find the loopholes).

## Binary Exploitation

You are given a binary (and sometimes source code) - crack it. Mess with heap, stack and many low-level tricks.

## Reverse Engineering

Haven't done many practices on this category yet. I consider it is quite similar to binary exploitation. Probably involves tools like IDA or Ghidra if the source code is not available.
