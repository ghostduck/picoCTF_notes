# Change your browser agent

Probably the best way is to use some plugins in browser.

Actually just any way to change the user-agent field would be OK.

I am too lazy to do that right now, so just use plain good old `wget`

`wget --user-agent=picobrowser https://jupiter.challenges.picoctf.org/problem/50522/flag`

Then the HTML file contains the flag.

## More about wget and HTTP Header

More HTTP header from [Who are you?](https://play.picoctf.org/practice/challenge/142?category=1&page=1)

They keep adding more requirements: referer, time (Only in 2018), enable "Do not track" on my site, need to fake a Swedish IP (have to search one and use the `X-Forwarded-For` field) and finally user language (`Accept-Language`, does not accept * and I have to search the code of Swedish...)

`wget http://mercury.picoctf.net:52362/ --user-agent=picobrowser --referer="http://mercury.picoctf.net:52362/" --header="Date: Mon, 09 Mar 2018 08:13:24 GMT" --header="DNT: 1" --header="X-Forwarded-For: 103.81.143.0" --header="Accept-Language: sv-SE;" -d`

At least I learnt to add new line of the header by using another `--header=`...

## With curl

`curl -v --user-agent picobrowser --referer "http://mercury.picoctf.net:52362/" http://mercury.picoctf.net:52362/ --header "Date: Mon, 09 Mar 2018 08:13:24 GMT" --header "DNT: 1" --header "X-Forwarded-For: 103.81.143.0" --header "Accept-Language: sv-SE;"`

Output extract:

```text
* Connected to mercury.picoctf.net (18.189.209.142) port 52362 (#0)
> GET / HTTP/1.1
> Host: mercury.picoctf.net:52362
> User-Agent: picobrowser
> Accept: */*
> Referer: http://mercury.picoctf.net:52362/
> Date: Mon, 09 Mar 2018 08:13:24 GMT
> DNT: 1
> X-Forwarded-For: 103.81.143.0
> Accept-Language: sv-SE;
>
< HTTP/1.1 200 OK
< Content-Type: text/html; charset=utf-8
< Content-Length: 1062
<

```

### curl with HEAD method

`curl -vvv  http://mercury.picoctf.net:15931/index.php -I`

Output extract:

```text
* Connected to mercury.picoctf.net (18.189.209.142) port 15931 (#0)
> HEAD /index.php HTTP/1.1
> Host: mercury.picoctf.net:15931
> User-Agent: curl/7.64.0
> Accept: */*
>
< HTTP/1.1 200 OK
HTTP/1.1 200 OK
< flag: picoCTF{flag_for_aHEAD}
flag: picoCTF{flag_for_aHEAD}
< Content-type: text/html; charset=UTF-8
Content-type: text/html; charset=UTF-8
```

### curl with cookies

From the Web Gauntlet problem.

```bash
curl 'http://jupiter.challenges.picoctf.org:54319/index.php' -X POST  -H 'Content-Type: application/x-www-form-urlencoded'  -H 'Cookie: PHPSESSID=XXXXfhjiXXXXp4ip4XXXXb8t06' --data-raw 'user=admin&pass=bocchi%27%3C%3E%27'
```
