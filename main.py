from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI()

# === [사용자 설정 정보] ===
# 본인의 정보를 정확히 입력하세요!
APP_KEY = "PSPMgzIS8seIx54DCJyqk0p7oTd4IpugLx4D"
APP_SECRET = "8XGCUgVJs8v47DE7/fXKcqj9e5F71FA9jiof6ucxwQR+L7bsBD3SQDEq6AMQM1gDpr78U8HeZSOpEgiM1TgugdvE5l2MLl15ZiIcPhs6rFGc4hhtyhX1ir3AQjh305Soe/Uav5pmcokKQqVPWL38dIpQ5g6HnymEwqMQjC8rTcxfnwitsG0="
CANO = "50157747"
ACNT_PRDT_CD = "01"         # 계좌번호 뒤 2자리 (보통 01)

URL_BASE = "https://openapivts.koreainvestment.com:29443" # 모의투자

# === [전역 변수: 토큰 저장소] ===
# 서버가 켜져있는 동안 발급받은 토큰을 여기에 저장해둡니다.
ACCESS_TOKEN = None 

# === [데이터 모델 정의] ===
class OrderRequestUS(BaseModel):
    code: str
    exchange: str
    qty: int
    price: float

# === [핵심 함수: 토큰 발급 및 관리] ===
def get_access_token():
    global ACCESS_TOKEN # 전역 변수를 사용하겠다고 선언
    
    # 1. 이미 발급받은 토큰이 있다면? API 요청 없이 그거 그냥 씁니다. (재사용)
    if ACCESS_TOKEN is not None:
        print("✅ 기존 토큰을 사용합니다.")
        return ACCESS_TOKEN
    
    # 2. 토큰이 없다면? 새로 발급받습니다.
    print("🔄 새 토큰 발급을 요청합니다...")
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    
    res = requests.post(f"{URL_BASE}/oauth2/tokenP", headers=headers, data=json.dumps(body))
    data = res.json()
    
    if "access_token" in data:
        ACCESS_TOKEN = data['access_token'] # 전역 변수에 저장!
        print(f"✅ 토큰 발급 성공! (앞부분: {ACCESS_TOKEN[:10]}...)")
        return ACCESS_TOKEN
    else:
        raise Exception(f"❌ 토큰 발급 실패! 원인: {data.get('error_description', data)}")

# === [서버 시작 이벤트] ===
# 서버(Uvicorn)가 켜질 때 딱 1번 실행됩니다.
@app.on_event("startup")
def startup_event():
    try:
        get_access_token() # 서버 켜자마자 토큰부터 받아놓음
    except Exception as e:
        print(f"⚠️ 시작 시 토큰 발급 실패: {e}")

# === [기능 1: 주식 현재가 조회] ===
@app.get("/price/{code}")
def get_current_price(code: str):
    try:
        token = get_access_token() # 저장된 토큰 가져옴
        headers = {
            "Authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": "FHKST01010100"
        }
        params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code}
        res = requests.get(f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price", 
                           headers=headers, params=params)
        return {
            "code": code,
            'price': float(res.json()['output']['stck_prpr']),
            "message": "조회 성공"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
# === [기능 1-2: 미국 주식 현재가 조회 (수정됨)] ===
# 사용법: /price/us/NAS/TSLA (나스닥, 테슬라)
@app.get("/price/us/{exchange}/{code}")
def get_us_price(exchange: str, code: str):
    try:
        token = get_access_token() # 저장된 토큰 사용
        
        headers = {
            "Authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            # 중요! 미국주식 현재가 조회용 TR_ID는 'HHDFS00000300' 입니다.
            "tr_id": "HHDFS00000300"
        }
        
        # 미국 주식 시세 URL은 domestic이 아니라 'overseas-price' 입니다.
        URL = f"{URL_BASE}/uapi/overseas-price/v1/quotations/price"
        
        params = {
            "AUTH": "", 
            "EXCD": exchange, # 거래소 코드 (NAS: 나스닥, NYS: 뉴욕, AMS: 아멕스)
            "SYMB": code      # 종목 코드 (TSLA, AAPL 등)
        }
        
        res = requests.get(URL, headers=headers, params=params)
        data = res.json()
        
        # 응답 데이터 구조 확인 및 가격 추출
        # 한국 주식은 'stck_prpr'이지만, 미국 주식은 'last'가 현재가입니다.
        if 'output' in data and 'last' in data['output']:
            current_price = data['output']['last']
            return {
                "code": code,
                "exchange": exchange,
                "price": float(current_price), # 숫자로 변환해서 전달
                "message": "조회 성공"
            }
        else:
            # API 에러 메시지 반환
            return {"status": "error", "message": data.get('msg1', '알 수 없는 오류')}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === [기능 2: 미국 주식 지정가 매수] ===
@app.post("/buy/us")
def buy_us_stock(order: OrderRequestUS):
    try:
        token = get_access_token() # 저장된 토큰 가져옴
        
        headers = {
            "Authorization": f"Bearer {token}",
            "appkey": APP_KEY,
            "appsecret": APP_SECRET,
            "tr_id": "VTTT1002U", 
            "custtype": "P",
        }
        
        body = {
            "CANO": CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "OVRS_EXCG_CD": order.exchange,
            "PDNO": order.code,
            "ORD_QTY": str(order.qty),
            "ORD_UNPR": str(order.price),
            "ORD_DVSN": "00",
            "ORD_SVR_DVSN_CD": "0",
        }
        
        res = requests.post(f"{URL_BASE}/uapi/overseas-stock/v1/trading/order",
                            headers=headers, data=json.dumps(body))
        
        result_data = res.json()
        
        if result_data['rt_cd'] == '0':
            return {
                "status": "success",
                "message": f"{order.exchange} {order.code} {order.qty}주 매수 주문 완료!",
                "data": result_data
            }
        else:
            return {
                "status": "fail",
                "message": result_data['msg1'],
                "error_code": result_data['msg_cd']
            }
    except Exception as e:
         return {"status": "error", "message": str(e)}