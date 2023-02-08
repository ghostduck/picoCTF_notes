# Client-side authentication is stupid

We have to prove it in some of the web exploitation CTF.

Most of them are just about reading the Javascript code from browser debug console.

Some complicated questions / JS requires deobfuscating the code...

## login

The POST request in form is overriden by and changed into a local JS function.

```javascript
const r = {
      u: 'input[name=username]',
      p: 'input[name=password]'
    },
    t = {
    };
    for (const e in r) t[e] = btoa(document.querySelector(r[e]).value).replace(/=/g, '');
    return 'YWRtaW4' !== t.u ? alert('Incorrect Username') : 'cGljb0NURns1M3J2M3JfNTNydjNyXzUzcnYzcl81M3J2M3JfNTNydjNyfQ' !== t.p ? alert('Incorrect Password') : void alert(`Correct Password! Your flag is ${ atob(t.p) }.`)

```

These are Base64 strings with trailing '=' removed. Even though the '=' doesn't matter in this question.

The answer is pretty obvious ...

<https://developer.mozilla.org/en-US/docs/Web/API/btoa>

> const encodedData = btoa("Hello, world"); // encode a string
> const decodedData = atob(encodedData); // decode the string

So we can just run `atob` to those two strings. (`atob()` is even shown in the `alert()` prompt...)

```javascript
const username = 'YWRtaW4';
const pwd = 'cGljb0NURns1M3J2M3JfNTNydjNyXzUzcnYzcl81M3J2M3JfNTNydjNyfQ';

atob(username);
atob(pwd);

// if there are encoding errors, add padding / trailing '=' to fit them
atob(username + "=");
atob(username + "==");
atob(username + "===");
atob(pwd + "=");
atob(pwd + "==");
atob(pwd + "===");
```

## Cookies

You can edit cookies at client-side. In Firefox, Inspect (F12) to open Developer Tools -> Storage -> Cookies

Maybe some attack/loopholes allow you to manipulate how the server gives you the cookies too.
