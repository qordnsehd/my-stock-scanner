import urllib.request
import time
from datetime import datetime

# 감시할 종목 (종목코드: 이름)
target_stocks = {
    '005930': '삼성전자',
    '000660': 'SK하이닉스',
    '035720': '카카오'
}

def get_stock_data(symbol):
    # 네이버 금융에서 데이터를 직접 가져오는 방식 (별도 설치 불필요)
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={symbol}&timeframe=day&count=40&requestType=0"
    try:
        response = urllib.request.urlopen(url)
        xml_data = response.read().decode('euc-kr')
        lines = xml_data.split('<item data="')[1:]
        prices = []
        for line in lines:
            val = line.split('"')[0].split('|')
            prices.append({
                'close': int(val[4]),
                'high': int(val[2]),
                'vol': int(val[5])
            })
        return prices
    except:
        return None

def analyze():
    print(f"\n[분석 시각: {datetime.now().strftime('%H:%M:%S')}]")
    for symbol, name in target_stocks.items():
        data = get_stock_data(symbol)
        if not data or len(data) < 21: continue

        curr = data[-1]  # 오늘 데이터
        prev = data[-2]  # 어제 데이터
        
        # 1. 소파동 언덕 (최근 20일 중 최고가)
        recent_20_high = max([x['high'] for x in data[-21:-1]])
        
        # 2. 돌파 조건 체크 (단테 소파동 돌파)
        is_breakout = curr['close'] > recent_20_high
        is_vol_up = curr['vol'] > (prev['vol'] * 1.1) # 테스트를 위해 조건을 낮춤

        print(f"[{name}] 분석 중... 현재가: {curr['close']}")
        
        if is_breakout:
            print(f"🔥 포착! [{name}] 소파동 돌파 확인!")
            print(f"   - 돌파가격(언덕): {recent_20_high}원")
            if is_vol_up:
                print(f"   - 거래량 동반: 확인됨 ({curr['vol']}주)")
        
    print("-" * 30)

# 시작 메시지
print("🚀 라이브러리 설치 없이 실행되는 '단테 감시기' 시작!")
while True:
    analyze()
    time.sleep(60) # 1분마다 반복
    