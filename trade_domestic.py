import requests
from config_loader import config
import report
import time
import json

APP_KEY = config['APP_KEY']
APP_SECRET = config['APP_SECRET']
ACCESS_TOKEN = ""
CANO = config['CANO']
ACNT_PRDT_CD = config['ACNT_PRDT_CD']
URL_BASE = config['URL_BASE']

def get_access_token():
    print("get access token")
    headers = {"content-type":"application/json"}
    body = {"grant_type":"client_credentials",
    "appkey":APP_KEY, 
    "appsecret":APP_SECRET}
    PATH = "oauth2/tokenP"
    URL = f"{URL_BASE}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    print(res)
    ACCESS_TOKEN = res.json()["access_token"]
    return ACCESS_TOKEN

def hashkey(datas):
    """암호화"""
    PATH = "uapi/hashkey"
    URL = f"{URL_BASE}/{PATH}"
    headers = {
    'content-Type' : 'application/json',
    'appKey' : APP_KEY,
    'appSecret' : APP_SECRET,
    }
    res = requests.post(URL, headers=headers, data=json.dumps(datas))
    hashkey = res.json()["HASH"]
    return hashkey


def get_current_price(code="000660"):
    """현재가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"FHKST01010100"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    }
    res = requests.get(URL, headers=headers, params=params)
    return int(res.json()['output']['stck_prpr'])

def get_target_price(code="000660"):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    PATH = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"FHKST01010400"}
    params = {
    "fid_cond_mrkt_div_code":"J",
    "fid_input_iscd":code,
    "fid_org_adj_prc":"1",
    "fid_period_div_code":"D"
    }
    res = requests.get(URL, headers=headers, params=params)
    stck_oprc = int(res.json()['output'][0]['stck_oprc']) #오늘 시가
    stck_hgpr = int(res.json()['output'][1]['stck_hgpr']) #전일 고가
    stck_lwpr = int(res.json()['output'][1]['stck_lwpr']) #전일 저가
    target_price = stck_oprc + (stck_hgpr - stck_lwpr) * 0.2
    return target_price

def get_stock_balance():
    print("get_stock_balance")
    PATH = "uapi/domestic-stock/v1/trading/inquire-balance"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8434R",
        "custtype":"P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    res = requests.get(URL, headers=headers, params=params)
    stock_list = res.json()['output1']
    evaluation = res.json()['output2']
    stock_dict = {}
    report.discord_message(f"====주식 보유잔고====")
    for stock in stock_list:
        if int(stock['hldg_qty']) > 0:
            stock_dict[stock['pdno']] = stock['hldg_qty']
            report.discord_message(f"{stock['prdt_name']}({stock['pdno']}): {stock['hldg_qty']}주")
            time.sleep(0.1)
    report.discord_message(f"주식 평가 금액: {evaluation[0]['scts_evlu_amt']}원")
    time.sleep(0.1)
    report.discord_message(f"평가 손익 합계: {evaluation[0]['evlu_pfls_smtl_amt']}원")
    time.sleep(0.1)
    report.discord_message(f"총 평가 금액: {evaluation[0]['tot_evlu_amt']}원")
    time.sleep(0.1)
    report.discord_message(f"=================")
    return stock_dict

def get_balance():
    print("view my account")
    PATH = "uapi/domestic-stock/v1/trading/inquire-psbl-order"
    URL = f"{URL_BASE}/{PATH}"
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC8908R",
        "custtype":"P",
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": "000660",
        "ORD_UNPR": "65500",
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_ICLD_YN": "Y",
        "OVRS_ICLD_YN": "Y"
    }
    res = requests.get(URL, headers=headers, params=params)
    print(res)
    cash = res.json()['output']['ord_psbl_cash']
    report.discord_message(f"주문 가능 현금 잔고: {cash}원")
    return int(cash)

def buy(code="000660", qty="1"):
    print("buy stock in market price")
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": str(int(qty)),
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0802U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        report.discord_message(f"[매수 성공]{str(res.json())}")
        return True
    else:
        report.discord_message(f"[매수 실패]{str(res.json())}")
        return False

def sell(code="000660", qty="1"):
    print("sell stock in market price")
    PATH = "uapi/domestic-stock/v1/trading/order-cash"
    URL = f"{URL_BASE}/{PATH}"
    data = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "PDNO": code,
        "ORD_DVSN": "01",
        "ORD_QTY": qty,
        "ORD_UNPR": "0",
    }
    headers = {"Content-Type":"application/json", 
        "authorization":f"Bearer {ACCESS_TOKEN}",
        "appKey":APP_KEY,
        "appSecret":APP_SECRET,
        "tr_id":"TTTC0801U",
        "custtype":"P",
        "hashkey" : hashkey(data)
    }
    res = requests.post(URL, headers=headers, data=json.dumps(data))
    if res.json()['rt_cd'] == '0':
        report.discord_message(f"[매도 성공]{str(res.json())}")
        return True
    else:
        report.discord_message(f"[매도 실패]{str(res.json())}")
        return False

"""reference use case code"""
def simple_korea_autotrade():
    try:
        print("simple_korea_autotrade")
        ACCESS_TOKEN = get_access_token()

        symbol_list = ["000660", "086790", "005930", "010120", "033100", "373220", "175330", "012450", "005490", "352820", "035420", "103140"] # 매수 희망 종목 리스트
        #000660(하이닉스)
        #086790(하나금융지주)
        #005930(삼성전자)
        #010120(LS일렉트릭)
        #033100(제룡전기)
        #373220(LG에너지솔루션)
        #175330(JB금융지주)
        #012450(한화에어로스페이스)
        #005490(포스코홀딩스)
        #352820(하이브)
        #035420(네이버)
        #103140(풍산)
        bought_list = [] # 매수 완료된 종목 리스트
        total_cash = get_balance() # 보유 현금 조회
        stock_dict = get_stock_balance() # 보유 주식 조회
        for sym in stock_dict.keys():
            bought_list.append(sym)
        target_buy_count = 3 # 매수할 종목 수
        buy_percent = 0.33 # 종목당 매수 금액 비율
        buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산
        soldout = False

        report.discord_message("===국내 주식 자동매매 프로그램을 시작합니다===")
        while True:
            t_now = datetime.datetime.now()
            t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
            t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=20, second=0,microsecond=0)
            today = datetime.datetime.today().weekday()
            if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
                report.discord_message("주말이므로 프로그램을 종료합니다.")
                break
            if t_9 < t_now < t_start and soldout == False: # 잔여 수량 매도
                for sym, qty in stock_dict.items():
                    sell(sym, qty)
                soldout == True
                bought_list = []
                stock_dict = get_stock_balance()
            if t_start < t_now < t_sell :  # AM 09:05 ~ PM 03:15 : 매수
                for sym in symbol_list:
                    if len(bought_list) < target_buy_count:
                        if sym in bought_list:
                            continue
                        target_price = get_target_price(sym)
                        current_price = get_current_price(sym)
                        report.discord_message(f"{sym} 의 목표가는 {target_price}, 현재가는 {current_price} 입니다")
                        if target_price < current_price:
                            buy_qty = 0  # 매수할 수량 초기화
                            buy_qty = int(buy_amount // current_price)
                            if buy_qty > 0:
                                report.discord_message(f"{sym} 목표가 달성({target_price} < {current_price}) 매수를 시도합니다.")
                                result = buy(sym, buy_qty)
                                if result:
                                    soldout = False
                                    bought_list.append(sym)
                                    get_stock_balance()
                        time.sleep(1)
                time.sleep(1)
                if t_now.minute == 30 and t_now.second <= 5: 
                    get_stock_balance()
                    time.sleep(5)
            if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
                if soldout == False:
                    stock_dict = get_stock_balance()
                    for sym, qty in stock_dict.items():
                        sell(sym, qty)
                    soldout = True
                    bought_list = []
                    time.sleep(1)
            if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
                get_stock_balance()
                report.discord_message("프로그램을 종료합니다.")
                break
    except Exception as e:
        report.discord_message(f"[오류 발생]{e}")
        time.sleep(1)