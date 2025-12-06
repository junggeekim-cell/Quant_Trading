import requests
import json

# === [내 정보 입력] ===
# 모의투자용 도메인입니다. (실전투자는 도메인이 다릅니다)
URL_BASE = "https://openapivts.koreainvestment.com:29443" 

# 발급받은 키를 여기에 붙여넣으세요
APP_KEY = "PSPMgzIS8seIx54DCJyqk0p7oTd4IpugLx4D"
APP_SECRET = "8XGCUgVJs8v47DE7/fXKcqj9e5F71FA9jiof6ucxwQR+L7bsBD3SQDEq6AMQM1gDpr78U8HeZSOpEgiM1TgugdvE5l2MLl15ZiIcPhs6rFGc4hhtyhX1ir3AQjh305Soe/Uav5pmcokKQqVPWL38dIpQ5g6HnymEwqMQjC8rTcxfnwitsG0="

# === [1. 접근 토큰(Access Token) 발급받기] ===
def get_access_token():
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    
    if res.status_code == 200:
        print("✅ 접속 성공! 토큰을 발급받았습니다.")
        return res.json()['access_token']
    else:
        print("❌ 접속 실패!")
        print(res.json())
        return None

# 실행
if __name__ == "__main__":
    token = get_access_token()
    if token:
        print(f"발급된 토큰(일부): {token[:20]}...")