from fastapi import FastAPI
import requests
import json

app = FastAPI()

# === [설정 정보] ===
# 본인의 키값으로 꼭 채워넣으세요!
APP_KEY = "PSPMgzIS8seIx54DCJyqk0p7oTd4IpugLx4D"
APP_SECRET = "8XGCUgVJs8v47DE7/fXKcqj9e5F71FA9jiof6ucxwQR+L7bsBD3SQDEq6AMQM1gDpr78U8HeZSOpEgiM1TgugdvE5l2MLl15ZiIcPhs6rFGc4hhtyhX1ir3AQjh305Soe/Uav5pmcokKQqVPWL38dIpQ5g6HnymEwqMQjC8rTcxfnwitsG0="
URL_BASE = "https://openapivts.koreainvestment.com:29443" # 모의투자용

# === [공통 함수: 토큰 발급] ===
# 실제 운영시에는 토큰을 한 번 발급받아 재사용하는 것이 좋지만, 
# 지금은 이해를 돕기 위해 요청마다 발급받는 간단한 구조로 갑니다.
def get_access_token():
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    res = requests.post(f"{URL_BASE}/oauth2/tokenP", headers=headers, data=json.dumps(body))
    return res.json()['access_token']

# === [기능 1: 주식 현재가 조회] ===
@app.get("/price/{code}")
def get_current_price(code: str):
    token = get_access_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100" # 주식 현재가 시세 조회용 트랜잭션 ID
    }
    
    # J : 주식, code : 종목코드
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": code
    }
    
    res = requests.get(f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price", 
                       headers=headers, params=params)
    
    data = res.json()
    
    # API 응답에서 현재가 추출 (문자열로 옴)
    current_price = data['output']['stck_prpr']
    name = "종목정보" # 실제 이름 조회 API는 별도지만 일단 생략
    
    return {
        "code": code,
        "price": int(current_price), # 숫자로 변환
        "message": "성공적으로 조회했습니다."
    }

# === [기능 2: 서버 상태 확인] ===
@app.get("/")
def read_root():
    return {"status": "Server is running", "system": "Quant Bot v1"}