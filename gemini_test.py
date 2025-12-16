import google.generativeai as genai
import json

# Gemini API 설정 (구글 클라우드나 AI Studio에서 키 발급 필요)
genai.configure(api_key="내_GEMINI_API_KEY")

def ask_gemini_trader(news_text, portfolio_status):
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = f"""
    당신은 냉철한 AI 펀드매니저입니다.
    
    [시장 데이터]
    {news_text}
    
    [내 자산 현황]
    {portfolio_status}
    
    위 정보를 바탕으로 매수(BUY), 매도(SELL), 관망(HOLD) 중 하나를 결정하고,
    반드시 아래 JSON 포맷으로만 답변하세요. 설명은 필요 없습니다.
    
    {{
        "decision": "BUY" | "SELL" | "HOLD",
        "ticker": "종목코드",
        "reason": "판단 이유 한 줄 요약",
        "quantity_percent": 10 (가용 현금의 몇 %를 쓸지, 또는 보유량의 몇 %를 팔지)
    }}
    """
    
    response = model.generate_content(prompt)
    
    # 응답에서 JSON만 추출 (가끔 말로 설명하는 것 방지)
    try:
        text = response.text
        start = text.find('{')
        end = text.rfind('}') + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except:
        return {"decision": "HOLD", "reason": "AI 응답 파싱 실패"}

# --- 테스트 실행 ---
news = "테슬라, 3분기 인도량 예상치 상회. 주가 급등 예상."
my_money = "현금 1000만원, 테슬라 없음"

decision = ask_gemini_trader(news, my_money)
print(decision)
# 결과 예시: {'decision': 'BUY', 'ticker': 'TSLA', 'reason': '인도량 호조로 상승 여력 있음', 'quantity_percent': 20}