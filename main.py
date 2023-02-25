import websocket, json, pprint, talib, numpy
from binance.client import Client
from binance.enums import *


api_key = "eUYIrgHHOXuIZD303Zb4pVXIleMCnstfLkQL8TdGKGpJqphHZJ6Nen1EB3ZpA4vI"
api_secret = "vhbLi9gs5Bi1jRjRWFLETn0suZ3Jw1nNbmSVdTXr1QhK3wcuhQcpcZmXY6ySlJZL"

client = Client(api_key,api_secret)

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_1s"


RSI_PERIOD = 14
RSI_OVERBOUGHT = 50
RSI_OVERSOLD = 40


TRADE_SYMBOL = "BTCUSDT"
TRADE_QUANTITY = 0.0005 #btcmiktari

closes = []
in_position = False


def binance_order(symbol, side, quantity, order_type=ORDER_TYPE_MARKET):
        try:
            print("Emir gonderildi.")
            order = client.create_order(symbol=symbol, side=side, quantity=quantity, type=order_type)
            print(order)
        except Exception as e:
            print("Bir hata olustu - {}".format(e))
            return False


def check_sell_or_buy(last_rsi):
    global in_position

    if last_rsi > RSI_OVERBOUGHT:
        if in_position:
            print("Asiri alim yeri fakat elimde yok.")
        else:
            print("Asiri alim yeri. SAT.")
            order_statu = binance_order(TRADE_SYMBOL, SIDE_SELL, TRADE_QUANTITY)
            if order_statu:
                in_position = False


    if last_rsi < RSI_OVERSOLD:
        if in_position:
            print("Asiri satis yeri fakat elimde var.")
        else:
            print("Asiri satis yeri. AL.")
            order_statu = binance_order(TRADE_SYMBOL, SIDE_BUY, TRADE_QUANTITY)
            if order_statu:
                in_position = True





def on_open(ws):
    print("Baglanti saglandi.")



def on_close(ws):
    print("Baglanti kapandi.")


def on_message(ws, message):
    print("Data geldi.")
    json_message = json.loads(message)
    # print(json_message)
    # pprint.pprint(json_message)
    candle = json_message['k']
    close = candle['c']
    is_candle_closed = candle['x']
    if is_candle_closed:
        print("Mum kapandi. BTC degeri: ", close)
        closes.append(float(close))
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes,RSI_PERIOD)
            print("simdiye kadar hesaplanan tüm RSIlar")
            print(rsi)
            last_rsi = rsi[-1]
            print("Gecerli RSI degeri: ", last_rsi)

            check_sell_or_buy(last_rsi)




ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()