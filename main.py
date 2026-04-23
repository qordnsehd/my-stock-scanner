import urllib.request
import re
import time
from datetime import datetime

def get_kospi_list():
    kospi_list = {}
    for page in range(1, 35): # 코스피 약 1700개 종목 수집
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page={page}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('cp949')
            items = re.findall(r'href="/item/main\.naver\?code=(\d{6})".*?>(.*?)</a>', html)
            if not items: break
            for code, name in items:
                kospi_list[code] = name
        except: break
        time.sleep(0.05)
    return kospi_list

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
    target_stocks = get_kospi_list()
    found_stocks = []
    
    for symbol, name in target_stocks.items():
        data = get_stock_data(symbol)
        if not data or len(data) < 224: continue

        curr = data[-1]
        prev = data[-2]
        
        # --- 이미지 속 조건들 구현 ---
        # 1. 이동평균선 계산
        ma5 = sum([x['close'] for x in data[-5:]]) / 5
        ma20 = sum([x['close'] for x in data[-20:]]) / 20
        ma60 = sum([x['close'] for x in data[-60:]]) / 60
        ma224 = sum([x['close'] for x in data[-224:]]) / 224

        # 2. 정배열 조건 (이미지 B, C, D항목 참고)
        is_aligned = ma5 > ma20 > ma60
        
        # 3. 소파동 언덕 돌파 (단테 기법)
        recent_20_high = max([x['high'] for x in data[-21:-1]])
        is_breakout = curr['close'] > recent_20_high
        
        # 4. 가격 범위 (이미지 A항목: 2000원 ~ 500,000원)
        is_price_range = 2000 <= curr['close'] <= 500000

        # 5. 거래량 폭발 (이미지 I항목: 150% 이상)
        is_vol_up = curr['vol'] > (prev['vol'] * 1.5)

        # 모든 조건 결합 (단테 224일선 돌파 + 정배열 + 거래량)
        if is_breakout and is_aligned and curr['close'] > ma224 and is_price_range and is_vol_up:
            found_stocks.append({
                'name': name, 'code': symbol, 'price': curr['close'], 
                'ma224': round(ma224), 'vol_ratio': round(curr['vol']/prev['vol'], 1)
            })
        time.sleep(0.01)

    # 웹페이지(HTML) 생성 로직
    html_content = f"""
    <html>
    <head><meta charset="utf-8"><title>단테X이미지 검색결과</title>
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; padding: 20px; background-color: #1a1a1a; color: white; }}
        table {{ border-collapse: collapse; width: 100%; background: #2d2d2d; }}
        th, td {{ border: 1px solid #444; padding: 12px; text-align: center; }}
        th {{ background-color: #e74c3c; color: white; }}
        .highlight {{ color: #f1c40f; font-weight: bold; }}
    </style></head>
    <body>
        <h1>🎯 단테 전략 + 이미지 조건식 포착</h1>
        <p>분석 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 코스피 전 종목 대상</p>
        <table>
            <tr><th>종목명</th><th>코드</th><th>현재가</th><th>224일선</th><th>거래량폭발</th></tr>
    """
    for s in found_stocks:
        html_content += f"<tr><td>{s['name']}</td><td>{s['code']}</td><td class='highlight'>{s['price']}원</td><td>{s['ma224']}원</td><td>{s['vol_ratio']}배</td></tr>"
    
    html_content += "</table><p>※ 조건: 정배열(5>20>60) + 224일선 돌파 + 20일 언덕 돌파 + 거래량 150%</p></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    run_scanner()
