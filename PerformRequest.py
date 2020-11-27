import requests
import json
import ast
import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
clients_lock = threading.Lock()
connected = 0

clients = {}
GameState = {}

def performApiRequest():
    baseurl = "https://tjda0mnl2k.execute-api.us-east-2.amazonaws.com"
    endpoint = "/DeployStage/"

    resp = requests.get(baseurl + endpoint)

    respJson = resp.json()

    firstJson = json.loads(respJson['body']) 
    
    firstJson = ast.literal_eval(str(firstJson["Items"]).strip('[]'))

    return firstJson
    

def matchMaking(jsonNeed):
    ARanker = []
    BRanker = []
    CRanker = []
    DRanker = []
    ERanker = []
    
    for i in range(len(jsonNeed)):
        #print("Player ID : " + jsonNeed[i]["PlayerID"]+ " AWR : " + jsonNeed[i]["AWR"] + " Wins : " + jsonNeed[i]["Win"] + " Loses : " + jsonNeed[i]["Lose"])
        if(float(jsonNeed[i]["AWR"]) >= 0.8):
            ARanker.append(jsonNeed[i])
        elif(float(jsonNeed[i]["AWR"]) >= 0.6):
            BRanker.append(jsonNeed[i])
        elif(float(jsonNeed[i]["AWR"]) >= 0.4):
            CRanker.append(jsonNeed[i])
        elif(float(jsonNeed[i]["AWR"]) >= 0.2):
            DRanker.append(jsonNeed[i])
        else:
            ERanker.append(jsonNeed[i])
    print("Number of ARankers found :", len(ARanker))
    if(len(ARanker) < 3):
        BRanker = BRanker + ARanker
    print("Number of BRankers found :", len(BRanker))
    if(len(BRanker) < 3):
        CRanker = CRanker + BRanker
    print("Number of CRankers found :", len(CRanker))    
    if(len(CRanker) < 3):
        DRanker = DRanker + CRanker    
    print("Number of DRankers found :", len(DRanker))
    if(len(DRanker) < 3):
        ERanker = ERanker + DRanker
    print("Number of ERankers found :", len(ERanker))
    matchMake(ARanker, "A Rank")
    matchMake(BRanker, "B Rank")
    matchMake(CRanker, "C Rank")
    matchMake(DRanker, "D Rank")
    matchMake(ERanker, "E Rank")

    
def matchMake(tempList, rankType):
    randNum = random.randint(1, 3)
    if(len(tempList) >= 3):
        print("-----------------------")
        print(rankType, " Players' fight.")
        if(randNum == 1):
            tempList[0]["Win"] = str(int(tempList[0]["Win"]) + 1)
            tempList[1]["Lose"]  = str(int(tempList[1]["Lose"]) + 1)
            tempList[2]["Lose"]  = str(int(tempList[2]["Lose"]) + 1)
            print("Player ID:", tempList[0]["PlayerID"], " Player Won!")
        elif(randNum == 2):
            tempList[1]["Win"] = str(int(tempList[1]["Win"])+ 1)
            tempList[0]["Lose"]  = str(int(tempList[0]["Lose"]) + 1)
            tempList[2]["Lose"]  = str(int(tempList[2]["Lose"]) + 1)
            print("Player ID:", tempList[1]["PlayerID"], " Player Won!")
        elif(randNum == 3):
            tempList[2]["Win"] = str(int(tempList[2]["Win"]) + 1)
            tempList[1]["Lose"]  = str(int(tempList[1]["Lose"]) + 1)
            tempList[0]["Lose"]  = str(int(tempList[0]["Lose"])+ 1)
            print("Player ID:", tempList[2]["PlayerID"], " Player Won!")
        print("-----------------------")
        addEditPlayers(tempList[0]["PlayerID"], tempList[0]["Win"], tempList[0]["Lose"])
        addEditPlayers(tempList[1]["PlayerID"], tempList[1]["Win"], tempList[1]["Lose"])
        addEditPlayers(tempList[2]["PlayerID"], tempList[2]["Win"], tempList[2]["Lose"])

        if(len(tempList) >= 3):
            matchMake(tempList[3:], rankType)

def addEditPlayers(playerid, win, lose):
    total = int(win) + int(lose)
    baseurl = "https://tjda0mnl2k.execute-api.us-east-2.amazonaws.com"
    endpoint = "/DeployStage/"
    headers = {"Player": "application/json"}
    data = {"PlayerID": {"S" : str(playerid)}, "AWR": {"S" : str(float(int(win) / total))}, "Win": {"S" : win}, "Lose" : {"S" : lose}}
    requests.put(baseurl + endpoint, data=json.dumps(data), headers=headers)

def connectionLoop(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        data = str(data)
        if addr in clients:
            if 'heartbeat' in data:
                clients[addr]['lastBeat'] = datetime.now()
        else:
            if 'connect' in data:
                clients[addr] = {}
                clients[addr]['lastBeat'] = datetime.now()
                clients[addr]['color'] = 0
                message = {"cmd": 0,"player":{"id":str(addr)}}
                m = json.dumps(message)
                for c in clients:
                    sock.sendto(bytes(m,'utf8'), (c[0],c[1]))

def cleanClients():
   while True:
      for c in list(clients.keys()):
         if (datetime.now() - clients[c]['lastBeat']).total_seconds() > 5:
            print('Dropped Client: ', c)
            clients_lock.acquire()
            del clients[c]
            clients_lock.release()
      time.sleep(1)

def gameLoop(sock):
   while True:
    clients_lock.acquire()
    mainJson = performApiRequest()
    matchMaking(mainJson)
    
    clients_lock.release()
    time.sleep(1)

def main():
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    start_new_thread(gameLoop, (s,))
    start_new_thread(connectionLoop, (s,))
    start_new_thread(cleanClients,())
    while True:
        time.sleep(1)
