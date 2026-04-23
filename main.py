import urllib.request
import time
from datetime import datetime

# 분석할 종목 리스트 (필요한 만큼 계속 추가 가능)
TARGET_STOCKS = {
    '005930': '삼성전자',
    '000660': 'SK하이닉스',
    '035720': '카카오',
    '005380': '현대차'
}

def get_stock_data(symbol):
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={symbol}&timeframe=day&count=250&requestType=0"
    try:
        response = urllib.request.urlopen(url)
        xml_data = response.read().decode('euc-kr')
        lines = xml_data.split('<item data="')[1:]
        prices = []
        for line in lines:
            val = line.split('"')[0].split('|')
            prices.append({'close': int(val[4]), 'high': int(val[2]), 'vol': int(val[5])})
        return prices
    except: return None

def run_scanner():
    print(f"🚀 [단테 검색기] 분석 시작: {datetime.now()}")
    for symbol, name in TARGET_STOCKS.items():
        data = get_stock_data(symbol)
        if not data or len(data) < 224: continue

        curr = data[-1]
        prev = data[-2]
        
        # 1. 소파동 언덕 (20일 고점)
        recent_20_high = max([x['high'] for x in data[-21:-1]])
        # 2. 224일선 (장기 이평)
        ma224 = sum([x['close'] for x in data[-224:]]) / 224

        # 돌파 조건 검사
        if curr['close'] > recent_20_high and curr['close'] > ma224:
            print(f"🔥 포착: {name} | 현재가: {curr['close']} | 언덕: {recent_20_high}")

if __name__ == "__main__":
    run_scanner()
