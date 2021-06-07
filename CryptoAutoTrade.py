from typing import Counter, Dict
import pyupbit
import time

매수퍼센트 = 3
손절퍼센트 = 3
익절퍼센트 = 5
트레이드카운트 = 0
listMaxLength = 2 #큐에 저장하는 데이터 개수 -> 가격. 9시부터 0.05초단위
head = 0 #데이터가 드가는위치 -> 큐
tail = 0 #데이터 나가는위치
list = [] # 데이터 

sell_loop_count = 0
ordered_coin_balance = 0

targetcoin = ''

buy = False
price=0



coinlist = pyupbit.get_tickers(fiat="KRW")
ban = ["KRW-BTC",
    "KRW-ETH",
    "KRW-BCH",
    "KRW-LTC",
    "KRW-BSV",
    "KRW-ETC",
    "KRW-BTG",
    "KRW-NEO",
    "KRW-STRK",
    "KRW-LINK",
    "KRW-BCHA",
    "KRW-DOT",
    "KRW-REP",
    "KRW-ATOM",
    "KRW-WAXP",
    "KRW-WAVES",
    "KRW-QTUM"]
coinlist=[item for item in coinlist if item not in ban]
#이름이 같으면 같은타입의 새로운 변수 생성

print(len(coinlist))

access = ""
secret = ""

upbit = pyupbit.exchange_api.Upbit(access, secret)
#25

while True:
    while(not buy):
        if(len(list)-head-1 >= 0):
            list.pop(head)
    #만약 29 | 29 라면 -> head=(head+1)%listMaxLength head 초기화. 아래 참조 
        list.insert(head,pyupbit.get_current_price(coinlist))
        if len(list)==listMaxLength: # 리스트가 30 개 찼을때.
            tail=(head+1) % listMaxLength  
            topPrice = 0
            for coinname in coinlist: 
                headPrice=list[head][coinname]
                tailPrice=list[tail][coinname]     
           
                #print(i," ",headPrice," ",headPrice-tailPrice," ",tailPrice/100*5," ")
                arbitrage=headPrice-tailPrice
                #익절퍼센트 -> 이율, 아래 조건문 * > * 이상 올라가면 매수.
                if arbitrage > tailPrice/100 * 매수퍼센트:
                    if arbitrage>topPrice:
                        topPrice=arbitrage
                        targetcoin=coinname
                    buy=True
            if buy:
                order = upbit.buy_market_order(targetcoin, 10000)
                    
                orderREQ = upbit.get_order(order['uuid'],state="done")
                time.sleep(0.1)
                while(orderREQ['trades_count'] == 0):
                    orderREQ = upbit.get_order(order['uuid'],state="done")
                    time.sleep(0.05)
                price=0
                time.sleep(0.05)
                
                트레이드카운트 = orderREQ['trades_count']
                for i in orderREQ['trades']:
                    price = price + float(i['price'])
                    ordered_coin_balance += float(i['volume'])  
                price /= 트레이드카운트
                print(price)
                """
                count = price/100 * 익절퍼센트
                calc=0
            
                if price<100:
                    calc = round(price - count,2)
                #100원 이하면 소수점 2자리까지, 값을 지정해줘야함
                
                elif price > 1000 :
                    calc=price+count-count%5 
                elif price > 10000:
                    calc=price+count-count%10                   
                elif price > 100000:
                    calc=price+count-count%50                  
                elif price > 500000:
                    calc=price+count-count%100                    
                elif price > 1000000:
                    calc=price+count-count%1000 
                
                #upbit.sell_limit_order(coinname, calc, ordered_coin_balance)
                """

        print("head",head," tail",tail," len",len(list))
        head=(head+1)%listMaxLength
        if(buy == False):
            for i in range(1,19):
                time.sleep(10)

    sell = False
    while(not sell):
        sell_loop_count += 1
        purchaseprice = pyupbit.get_current_price(targetcoin)
        if purchaseprice == None:
            break

        # 5퍼 이상일때 매도
        if purchaseprice - price > price/100 * 익절퍼센트:
            upbit.sell_market_order(targetcoin, ordered_coin_balance)
            ordered_coin_balance = 0
            sell=True
            buy=False
            break

        # -2퍼 이하 매도
        if price - purchaseprice > price/100 * 손절퍼센트:
            upbit.sell_market_order(targetcoin, ordered_coin_balance)
            ordered_coin_balance = 0
            """
            for i in upbit.get_order(targetcoin):
            # i === targetCoin의 거래내역 -> 가격
            
           # 매수 -> 매도리스트 -> 매수한가격 - 매도한가격 = 0 -> 엑셀
                upbit.cancel_order(i['uuid'])
                upbit.sell_market_order(targetcoin, upbit.get_balance(targetcoin))
            """
            sell=True
            buy=False
            break
        
        #sell_loop가 20분동안 돌고 있으면.
        if(sell_loop_count == 6000):
            upbit.sell_market_order(targetcoin, ordered_coin_balance)
            ordered_coin_balance = 0
            sell=True
            buy=False
            break
        time.sleep(0.2)
