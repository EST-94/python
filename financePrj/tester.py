import FinanceDataReader as web
# need pandas-datareader, bs4
from datetime import date, timedelta
import matplotlib.pyplot as plt
import datetime
import pandas as pd
from urllib.parse import urlparse
import json
import re
import cgi


from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading


PORT_NUMBER = 8666
market = ""
dayago = ""



class reqHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        # ex) http://localhost:8666/finance/basicset?where=NASDAQ&from=180


        if None != re.search('/finance/*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if None != re.search('/finance/basicset/*', self.path):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                queryString = urlparse.split('&')
                market = queryString[0].split('=')[1]
                dayago = queryString[1].split('=')[1]



                if ctype == 'application/json':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    receivedData = post_data.decode('utf-8')
                    print(type(receivedData))
                    tempDict = json.loads(receivedData)

                    if setParams(tempDict) == True:
                        tempDict.append("request adjusted. selected market = ", market, "selected dayago = ", dayago)
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    else:
                        tempDict.append("request failed, check ur status again.")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                        
         else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        return

    def do_GET(self):
        print("request accepted, constructing result datas..")
        # 결과창 : "종목명"(종목코드), 매수/매도추천여부(점수) 출력
        # ex) http://localhost:8666/finance/showRes?how=(buy/sell)&duration=(long/short)&recommand=(on/off)&stockcode=(AAPL_TSLA)
        # 추천은 변동폭 기준 전망이 좋은 상위 10개 종목 내용 추가함. 타 조건과 겹칠 수 있다.
        # 매수 / 매도 옵션에 따라 적용되는 식을 다르게 한다. 검색하는 코드들만 내용 출력할 것.
        data = []
        if None != re.search('/finance/*', self.path):
            if None != re.search('finance/showRes', self.path):

                queryString = urlparse.split('&')
                modSet = queryString[0].split('=')[1]
                rangeSet = queryString[1].split('=')[1]
                recommandSet = queryString[2].split('=')[1]
                targetStock = queryString[3].split('=')[1]
                #                 switchs = [modSet, rangeSet, searchSet]

                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    if resultData == None:
                        print("no data exists.")
                        data.append("no data exists.")
                    else:
                        for i in range(0, resultData):
                            print(resultData[i].__dict__)
                            data.append(resultData[i].__dict__)

                except:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    data.append("Errors occured : values out of condition, check your request again.")

                finally:
                    self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

            elif None != re.search('/finance/generateList', self.path):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                t = threading.Thread(target=createData)
                t.start()
                data.append("{listing is underway:check ur server console and initalize settings.}")
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                data.append("{info:no such api}")
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):

    try:

        # Create a web server and define the handler to manage the
        # incoming request
        # server = ThreadedHTTPServer(('', PORT_NUMBER), myHandler)
        server = HTTPServer(('', PORT_NUMBER), reqHandler)
        print('Started httpserver on port ', PORT_NUMBER)

        # initSvr()
        # Wait forever for incoming http requests
        server.serve_forever()

    except (KeyboardInterrupt, Exception) as e:
        print('^C received, shutting down the web server')
        print(e)
        server.socket.close()
