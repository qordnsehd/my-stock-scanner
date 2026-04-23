import urllib.request
import re
import time
from datetime import datetime

def get_kospi_list():
    """네이버 증권에서 코스피 상장사 리스트를 자동으로 가져옵니다."""
    kospi_list = {}
    for page in range(1, 35):
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page={page}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('cp949')
            items = re.findall(r'href="/item/main\.naver\?code=(\d{6})".*?>(.*?)</a>', html)
            if not items: break
            for code, name in items: kospi_list[code] = name
        except: break
        time.sleep(0.01)
    return kospi_list

def get_stock_data(symbol):
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={symbol}&timeframe=day&count=300&requestType=0"
    try:
        req = urllib.request.urlopen(url)
        xml_data = req.read().decode('euc-kr')
        lines = xml_data.split('<item data="')[1:]
        return [{'close': int(val.split('|')[4]), 'high': int(val.split('|')[2]), 'vol': int(val.split('|')[5])} 
                for val in [line.split('"')[0] for line in lines]]
    except: return None

def run_scanner():
    kospi_stocks = get_kospi_list()
    found_stocks = []
    print(f"🚀 코스피 {len(kospi_stocks)}개 전 종목 정밀 분석 시작...")

    for symbol, name in kospi_stocks.items():
        data = get_stock_data(symbol)
        if not data or len(data) < 224: continue
        
        curr, prev = data[-1], data[-2]
        ma224 = sum([x['close'] for x in data[-224:]]) / 224
        recent_20_high = max([x['high'] for x in data[-21:-1]])
        
        # 단테 기법 핵심 필터: 224일선 위 + 20일 언덕 돌파 + 거래량 폭발
        if curr['close'] > recent_20_high and curr['close'] > ma224:
            if curr['vol'] > prev['vol'] * 1.5:  # 거래량 150% 이상만 추림
                found_stocks.append({
                    'name': name, 'code': symbol, 'price': f"{curr['close']:,}", 
                    'ma224': f"{int(ma224):,}", 'vol_ratio': round(curr['vol']/prev['vol'], 1)
                })
        time.sleep(0.02) # 차단 방지용 미세 지연

    # --- 실시간 대시보드 HTML 생성 ---
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>단테 밥그릇 검색기 Pro</title>
        <style>
            body {{ background: #0b0e14; color: #e1e1e1; font-family: 'Pretendard', sans-serif; margin: 0; padding: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f23645; padding-bottom: 15px; margin-bottom: 20px; }}
            .title {{ color: #f23645; font-size: 20px; font-weight: bold; }}
            .count {{ background: #2a2e39; padding: 5px 12px; border-radius: 20px; font-size: 14px; }}
            .card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }}
            .card {{ background: #1e222d; border-radius: 12px; padding: 20px; border: 1px solid #2a2e39; }}
            .name {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #fff; }}
            .price {{ font-size: 24px; color: #f23645; font-weight: 800; margin-bottom: 10px; }}
            .info {{ font-size: 13px; color: #848e9c; display: flex; justify-content: space-between; }}
            .vol-badge {{ background: rgba(242, 54, 69, 0.1); color: #f23645; padding: 2px 8px; border-radius: 4px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">🎯 단테 밥그릇 포착</div>
            <div class="count">포착: {len(found_stocks)}개</div>
        </div>
        <p style="font-size: 12px; color: #848e9c;">업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (코스피 전체 분석)</p>
        <div class="card-grid">
    """
    for s in found_stocks:
        html_content += f"""
            <div class="card">
                <div class="name">{s['name']} <span style="font-size:12px; font-weight:normal;">{s['code']}</span></div>
                <div class="price">{s['price']}원</div>
                <div class="info">
                    <span>224일선: {s['ma224']}원</span>
                    <span class="vol-badge">거래량 {s['vol_ratio']}배 🔥</span>
                </div>
            </div>
        """
    html_content += "</div></body></html>"
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)

if __name__ == "__main__": run_scanner()
