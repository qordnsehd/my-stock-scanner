import urllib.request
import re
import time
from datetime import datetime

def get_kospi_list():
    """네이버 증권에서 코스피 종목 리스트를 가져옵니다."""
    print("📦 코스피 종목 리스트를 불러오는 중...")
    kospi_list = {}
    # 코스피 페이지(1~40페이지 정도)를 훑어서 종목코드와 이름을 추출합니다.
    for page in range(1, 35):
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page={page}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('cp949')
            # 정규표현식으로 종목코드와 이름 추출
            items = re.findall(r'href="/item/main\.naver\?code=(\d{6})".*?>(.*?)</a>', html)
            if not items: break
            for code, name in items:
                kospi_list[code] = name
        except: break
        time.sleep(0.1)
    print(f"✅ 총 {len(kospi_list)}개 종목 수집 완료.")
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
    print(f"🚀 [단테 검색기] {len(target_stocks)}개 종목 분석 시작: {datetime.now()}")
    print("-" * 50)
    
    found_count = 0
    for symbol, name in target_stocks.items():
        data = get_stock_data(symbol)
        if not data or len(data) < 224: continue

        curr = data[-1]
        prev = data[-2]
        
        # 1. 소파동 언덕 (최근 20일 고점)
        recent_20_high = max([x['high'] for x in data[-21:-1]])
        # 2. 224일선 (장기 이평)
        ma224 = sum([x['close'] for x in data[-224:]]) / 224

        # [조건] 224일선 위에 있으면서, 최근 20일 언덕을 돌파할 때
        if curr['close'] > recent_20_high and curr['close'] > ma224:
            # 거래량이 전일 대비 1.5배 이상일 때만 출력 (필터링)
            if curr['vol'] > (prev['vol'] * 1.5):
                print(f"🔥 [포착] {name}({symbol}) | 현재가: {curr['close']} | 언덕: {recent_20_high} | 거래량: {round(curr['vol']/prev['vol'], 1)}배")
                found_count += 1
        
        # 깃허브 서버 과부하 방지 및 차단 방지
        time.sleep(0.05)

    print("-" * 50)
    print(f"✅ 분석 완료! 총 {found_count}개 종목이 조건에 포착되었습니다.")

if __name__ == "__main__":
    run_scanner()
