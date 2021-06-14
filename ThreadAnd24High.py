from typing import Counter, Dict
import pyupbit
import time
import threading as TH


access = ""
secret = ""
upbit = pyupbit.exchange_api.Upbit(access, secret)

sellThreadCount = 0
tradesCount = 0
listMaxLength = 2 #큐에 저장하는 데이터 개수 -> 가격. 9시부터 0.05초단위
head = 0 #데이터가 드가는위치 -> 큐
tail = 0 #데이터 나가는위치
list = [] # 데이터 

sell_loop_count = 0
ordered_coin_balance = 0
maxOrder = 2

targetcoin = ''
isTimerOn = True

buy = False
price=0
def threeMinTimer():
    global buy3Min
    global isTimerOn
    while(isTimerOn):
        for i in range(1,7):
            time.sleep(10)
        buy3Min = True

def reFreshPriceList(coinName):
    try:
        for i in orderedList[coinName]:
            i(headPrice)
    except Exception:
        pass

class Seller(TH.Thread):
    orderedPrice=0
    orderedVolume=0
    currentPrice=0
    sell_loop_count=0
    coinName=''
    def __init__(self,ordered,volume,name):
        TH.Thread.__init__(self)
        self.orderedPrice = ordered
        self.orderedVolume = volume
        self.coinName = name
        global sellThreadCount
        sellThreadCount += 1
    def refresh(self,price):
        self.currentPrice=price
    def run(self):
        global upbit
        global sellThreadCount
        global orderedList
        while(True):            
            self.sell_loop_count+=1
            if self.currentPrice == None:
                break
            # N퍼 이상일때 매도
            if self.currentPrice - self.orderedPrice > self.orderedPrice/100 * 2:
                upbit.sell_market_order(self.coinName, self.orderedVolume)
                orderedList[coinname].remove(refresh)
                list = []
                sellThreadCount-=1
                break
            # -N퍼 이하 매도
            if self.orderedPrice - self.currentPrice > self.orderedPrice/100 * 2.5:
                upbit.sell_market_order(self.coinName, self.orderedVolume)
                sellThreadCount-=1
                orderedList[coinname].remove(refresh)
                list = []
                break
            if(self.sell_loop_count == 900):
                upbit.sell_market_order(self.coinName, self.orderedVolume)
                sellThreadCount-=1
                orderedList[coinname].remove(refresh)
                list = []
                break
            time.sleep(0.2)
    
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

orderedList={}
for i in coinlist:
    orderedList[i] = []
print(len(coinlist))

#25
temp = TH.Thread(target= threeMinTimer)
temp.setDaemon(True)
temp.start()

try:
    while(True):
        ordered_coin_balance=0
        if(len(list)-head-1 >= 0):
            list.pop(head)
    #만약 29 | 29 라면 -> head=(head+1)%listMaxLength head 초기화. 아래 참조 
        list.insert(head,pyupbit.get_current_price(coinlist))
        if len(list)==listMaxLength: #리스트가 다 찼을 때
            tail=(head+1) % listMaxLength  
            topPrice = 0
            for coinname in coinlist: 
                headPrice=list[head][coinname]
                tailPrice=list[tail][coinname]
                TH.Thread(target= reFreshPriceList,args= (coinname,)).start()
    
                #print(i," ",headPrice," ",headPrice-tailPrice," ",tailPrice/100*5," ")
                arbitrage=headPrice-tailPrice
                #익절퍼센트 -> 이율, 아래 조건문 * > * 이상 올라가면 매수.
                if arbitrage > tailPrice/100 * 2:
                    if arbitrage>topPrice:
                        topPrice=arbitrage
                        targetcoin=coinname
                    buy=True
            #print(maxOrder > sellThreadCount, "|", maxOrder, "|", sellThreadCount)
            if buy and buy3Min and (maxOrder > sellThreadCount) :
                order = upbit.buy_market_order(targetcoin, 15000)
                orderREQ = upbit.get_order(order['uuid'],state="done")
                time.sleep(0.05)
                while(orderREQ['trades_count'] == 0):
                    orderREQ = upbit.get_order(order['uuid'],state="done")
                price=  0
                time.sleep(0.05)
                tradesCount = orderREQ['trades_count']
                for i in orderREQ['trades']:
                    price = price + float(i['price'])
                    ordered_coin_balance += float(i['volume'])  
                price /= tradesCount
                seller = Seller(price,ordered_coin_balance,targetcoin)
                seller.start()
                orderedList[targetcoin].append(seller.refresh)
                buy = False
                buy3Min = False
                #print(price)
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
        for i in range(1,7):
            time.sleep(10)
except KeyboardInterrupt or Exception:
    isTimerOn = False
        
        
        