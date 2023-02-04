# Flag shop - the signed 32 bit integer

The trick and bug is about use of signed integer.

## Question

The C source code:

```c
#include <stdio.h>
#include <stdlib.h>
int main()
{
    setbuf(stdout, NULL);
    int con;
    con = 0;
    int account_balance = 1100;
    while(con == 0){

        printf("Welcome to the flag exchange\n");
        printf("We sell flags\n");

        printf("\n1. Check Account Balance\n");
        printf("\n2. Buy Flags\n");
        printf("\n3. Exit\n");
        int menu;
        printf("\n Enter a menu selection\n");
        fflush(stdin);
        scanf("%d", &menu);
        if(menu == 1){
            printf("\n\n\n Balance: %d \n\n\n", account_balance);
        }
        else if(menu == 2){
            printf("Currently for sale\n");
            printf("1. Defintely not the flag Flag\n");
            printf("2. 1337 Flag\n");
            int auction_choice;
            fflush(stdin);
            scanf("%d", &auction_choice);
            if(auction_choice == 1){
                printf("These knockoff Flags cost 900 each, enter desired quantity\n");

                int number_flags = 0;
                fflush(stdin);
                scanf("%d", &number_flags);
                if(number_flags > 0){
                    int total_cost = 0;
                    total_cost = 900*number_flags;
                    printf("\nThe final cost is: %d\n", total_cost);
                    if(total_cost <= account_balance){
                        account_balance = account_balance - total_cost;
                        printf("\nYour current balance after transaction: %d\n\n", account_balance);
                    }
                    else{
                        printf("Not enough funds to complete purchase\n");
                    }
                }
            }
            else if(auction_choice == 2){
                printf("1337 flags cost 100000 dollars, and we only have 1 in stock\n");
                printf("Enter 1 to buy one");
                int bid = 0;
                fflush(stdin);
                scanf("%d", &bid);

                if(bid == 1){

                    if(account_balance > 100000){
                        FILE *f = fopen("flag.txt", "r");
                        if(f == NULL){

                            printf("flag not found: please run this on the server\n");
                            exit(0);
                        }
                        char buf[64];
                        fgets(buf, 63, f);
                        printf("YOUR FLAG IS: %s\n", buf);
                        }

                    else{
                        printf("\nNot enough funds for transaction\n\n\n");
                    }}

            }
        }
        else{
            con = 1;
        }

    }
    return 0;
}
```

In short, we can get the flag if we can have balance greater than 100000 or use some ways else. (By the way 65535 uses 16 bit)

At first sight without reading the hint, I really tried to do something like buffer overflow ... Well, I failed. And generic problems are not the category for all those buffer overflow tricks.

After reading the hint - Two's complement. I remember the horrible bug I have written in C++:

```c
unsigned int i = length_of_something;

while i <= 0 {
    // do something
    int k = arr[i]; // One of those big problem is using i as index
    --i;
}

```

The program crashed after i becomes 0 and then --i runs -- i becomes `4294967295`, which is `-1` in two's complement.

And the bug we can exploit is in these lines:

```c
    total_cost = 900*number_flags;
    if(total_cost <= account_balance){
        account_balance = account_balance - total_cost;
```

`total_cost` is signed integer. As long as we made the first bit of it `1`, it becomes a negative number. Minus a negative number would be a plus to the `account_balance`!

So we can just craft the `number_flags` such that 900*`number_flags` would be 1000_0000_0001_0000_0000_0000_0000_0000 (Single 1, 10 0s, one 1, and 20 0s)

```python
>>> 0b1000_0000_0001_0000_0000_0000_0000_0000
2148532224
# Formating: 2,148,532,224
>>> 2148532224 // 900
2387258
>>> 0b1_0000_0000_0000_0000_0000  # 1 1, 20 0s
1048576
```

```text
These knockoff Flags cost 900 each, enter desired quantity
2387258 # (My input)

The final cost is: -2146435096
# Formatting: -2,146,435,096

Your current balance after transaction: 2146436196
# EZ Clap
```

## Reminder of Two's complement

For 4 bits of integer in Two's complement

0111  7
...
0000  0
1111 -1
1110 -2
1101 -3
1100 -4
1011 -5
1010 -6
1001 -7
1000 -8

One bit is used for sign bit so we can only use remaining 3 bits for the value. (between 7 and -8)

Quick calculation: 1000 is negative 2^3 -> negative 8 -> -8
Then we just add the other bits to -8 as usual. (Just like -8 + x. When x is 1, we have -8+1 =-7)
