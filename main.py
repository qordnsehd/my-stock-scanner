import urllib.request
import re
import time
from datetime import datetime

def get_kospi_list():
    kospi_list = {}
    for page in range(1, 35):
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
    target_stocks = get_kospi_list()
    found_stocks = []
    
    for symbol, name in target_stocks.items():
        data = get_stock_data(symbol)
        if not data or len(data) < 224: continue

        curr, prev = data[-1], data[-2]
        recent_20_high = max([x['high'] for x in data[-21:-1]])
        ma224 = sum([x['close'] for x in data[-224:]]) / 224

        if curr['close'] > recent_20_high and curr['close'] > ma224 and curr['vol'] > (prev['vol'] * 1.5):
            found_stocks.append({
                'name': name, 'code': symbol, 'price': curr['close'], 
                'high': recent_20_high, 'vol_ratio': round(curr['vol']/prev['vol'], 1)
            })
        time.sleep(0.01)

    # HTML 파일 생성
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>단테 검색기 결과</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; background-color: #f4f7f6; }}
            table {{ border-collapse: collapse; width: 100%; background: white; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>🔥 단테 조건 검색 포착 종목</h1>
        <p>최종 분석 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <table>
            <tr><th>종목명</th><th>코드</th><th>현재가</th><th>언덕(20일고점)</th><th>거래량비율</th></tr>
    """
    for s in found_stocks:
        html_content += f"<tr><td>{s['name']}</td><td>{s['code']}</td><td>{s['price']}원</td><td>{s['high']}원</td><td>{s['vol_ratio']}배</td></tr>"
    
    html_content += "</table></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    run_scanner()
