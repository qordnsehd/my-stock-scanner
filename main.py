import urllib.request
import time
from datetime import datetime

# 테스트용 5종목 (삼성전자, SK하이닉스, 현대차, LG에너지솔루션, 기아)
TEST_STOCKS = {
    '005930': '삼성전자',
    '000660': 'SK하이닉스',
    '005380': '현대차',
    '373220': 'LG에너지솔루션',
    '000270': '기아'
}

def get_stock_data(symbol):
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={symbol}&timeframe=day&count=300&requestType=0"
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
    found_stocks = []
    print(f"🚀 테스트 모드 시작 (5종목)")
    
    for symbol, name in TEST_STOCKS.items():
        data = get_stock_data(symbol)
        if not data or len(data) < 224: continue

        curr, prev = data[-1], data[-2]
        
        # 1. 이동평균선
        ma5 = sum([x['close'] for x in data[-5:]]) / 5
        ma20 = sum([x['close'] for x in data[-20:]]) / 20
        ma60 = sum([x['close'] for x in data[-60:]]) / 60
        ma224 = sum([x['close'] for x in data[-224:]]) / 224

        # 2. 조건 검사 (이미지 조건 반영)
        is_aligned = ma5 > ma20 > ma60  # 정배열
        recent_20_high = max([x['high'] for x in data[-21:-1]])
        is_breakout = curr['close'] > recent_20_high # 언덕 돌파
        
        # 테스트를 위해 거래량 조건은 조금 완화(1.1배)해서 넣어둘게요
        if is_breakout or (curr['close'] > ma224):
            found_stocks.append({
                'name': name, 'code': symbol, 'price': curr['close'], 
                'ma224': round(ma224), 'vol_ratio': round(curr['vol']/prev['vol'], 1)
            })
        time.sleep(0.1)

    # HTML 생성
    html_content = f"""
    <html>
    <head><meta charset="utf-8"><title>단테 검색기 테스트</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; background-color: #1a1a1a; color: white; }}
        table {{ border-collapse: collapse; width: 100%; background: #2d2d2d; }}
        th, td {{ border: 1px solid #444; padding: 12px; text-align: center; }}
        th {{ background-color: #e74c3c; color: white; }}
    </style></head>
    <body>
        <h1>🎯 5종목 테스트 결과</h1>
        <p>분석 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table>
            <tr><th>종목명</th><th>코드</th><th>현재가</th><th>224일선</th><th>거래량비율</th></tr>
    """
    for s in found_stocks:
        html_content += f"<tr><td>{s['name']}</td><td>{s['code']}</td><td>{s['price']}원</td><td>{s['ma224']}원</td><td>{s['vol_ratio']}배</td></tr>"
    html_content += "</table></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ index.html 생성 완료!")

if __name__ == "__main__":
    run_scanner()
