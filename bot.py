import json
import requests
import time
import urllib
import random
from db import DBHelper
import threading
db = DBHelper()
import config
URL = "https://api.telegram.org/bot{}/".format(config.token)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js
	
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def isadmin(chat,user):
    if user == 139468375:
        return "administrator"
    else:    
        url = URL + "getChatMember?chat_id={0}&user_id={1}".format(chat,user)
        js = get_json_from_url(url)
        if len(js["result"]) > 0:
            return js["result"]["status"]

       
def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def logger (chat, tag, message):
    db = DBHelper()
    chatnum = str(chat)
    chatnum = chatnum.replace('-', '')
    tag = tag.upper()
    if tag == "NEWCHAT":
        msg = "#{0} - #chat{1}\n {2}".format(tag,chatnum,message)
        send_message(msg,"-185877423")
    elif tag == "ROGUEBONER":
        if chatnum == "1001068468795":
            print("{0}".format(message))
    else:
        if chat == "0":
            msg = "#INFO - #{0}\n{1}".format(tag,message)
            send_message(msg,"-185877423")
        else:
            loggingon = str(db.get(chat, "logging")[0])
            chatname = str(db.get(chat, "chat_name")[0])
            if loggingon.lower() == "true":
                logging = str(db.get(chat,tag.lower())[0])
                if logging.lower() == "true":
                    msg = "#{0} - #chat{1} - {2}\n {3}".format(tag,chatnum,chatname,message)
                    send_message(msg,"-185877423")
            #else:
                #msg = "#chat{0} - {1} \n logging disabled".format(chatnum,chatname)
                #send_message(msg,"-185877423")
def handlemessages(updates):
    for update in updates["result"]:
        try:
            chat = update["message"]["chat"]["id"]
            user = update["message"]["from"]["id"]
            if chat == user:
                send_message("Sorry, Duckhunt is not available in private chats.", chat)
            else:
                text = update["message"]["text"].lower()
                chatname = update["message"]["chat"]["title"]
                username = update["message"]["from"]["first_name"]
                newchat = db.newchat(chat)
                isnew = [0]
                if newchat == isnew:
                    logger(chat, "newchat", "chat {0} is new.".format(chatname))
                    db.setup(chat, chatname)
                newuser = db.newuser(chat, user)
                if newuser == isnew:
                    logger(chat, "newuser", "user {0} is new.".format(username))
                    db.adduser(chat,user)
                userlevel = isadmin(chat, user)
                duckenabled = str(db.get(chat, "duckenabled")[0])
                duckdeployed = str(db.get(chat, "duckdeployed")[0])    
                logging = str(db.get(chat, "logging")[0])    
#help   
                if text == "/help@duckhunt_bot":
                    send_message("HELP:\n!bang OR .bang OR /bang - shoot a duck when one is out. Shooting when there is no duck will lose you points.\n\nAdmin commands:\n/duckenabled <true|false> - Enables or disables the duckhunt game in the chat.\n/ducktime <30-360> - Amount of time in minutes between rolling for a duck.\n/duckprob <1-99> - Probability of a duck being deployed on each roll in percent.\n/duckwaittime - Amount of time in minutes a duck will hang around before flying away.\n/duckcall - Immediately rolls for a duck. Probablity still applies and the timer will reset.\n", chat)
                elif text == "/score":
                    score = db.scoreget(chat, user)
                    score = score[0]
                    send_message("Your score is {0}".format(score), chat)    
                     
#duckenabled                
                elif text.startswith("/duckenabled"):
                        if userlevel in ["administrator","creator"]:
                            if  (len(text.split())) == 1:
                                got = db.get(chat, "duckenabled")
                                got = str(got[0])
                                send_message(got, chat)
                            elif  (len(text.split())) == 2:
                                argument = "duckenabled"
                                value = text.split()[1]
                                if value in ["true","false"]:
                                    value = value.lower()     
                                    logger(chat,"setting","Set duckenabled {0}".format(value))                                    
                                    send_message("set {0} to {1}".format(argument, value), chat)
                                    db.set(chat, argument, value)
                                else:
                                    send_message("{0} is not a valid setting. it must be either 'true' or 'false'.".format(value), chat)
                            else:
                                send_message("Missing/wrong argument. Usage: /duckenabled <true/false>", chat)
                        else:
                            send_message("You do not have permission to use this command. You are: {0}.".format(userlevel), chat)
                            
############ only active when duckhunt is enabled. 
                     
                if duckenabled.lower() == "true":
#bang                
                    if text in ["!bang",".bang","/bang"]:
                        if duckdeployed == "True":
                            logger(chat,"shots","Duck deployed.")
                            score = db.scoreget(chat, user)
                            score = score[0]
                            score = score + 1 
                            db.scoreset(chat, user, score)
                            send_message("{0} shot the duck! Current score: {1}".format(username,score), chat)
                            
                            db.set(chat, "duckdeployed", False)
                            setnextroll(chat)
                        else:
                            logger(chat,"shots","No Duck deployed.")
                            score = db.scoreget(chat, user)
                            score = score[0]
                            score = score - 1 
                            db.scoreset(chat, user, score)
                            send_message("There is no duck right now {0}! You lose a point! Current score: {1}".format(username,score), chat)

                            
############ these need to be admin only. 
                                  
#duckcall                            
                    elif text == "/duckcall": 
                        if userlevel in ["administrator","creator"]:
                            duck_roll(chat)
                        else:
                            send_message("You do not have permission to use this command. You are: {0}.".format(userlevel), chat)
#duckprob                        
                    elif text.startswith("/duckprob"):
                        if userlevel in ["administrator","creator"]:
                            if  (len(text.split())) == 1:
                                got = db.get(chat, "duckprob")
                                got = str(got[0])
                                send_message(got, chat)
                            elif  (len(text.split())) == 2:
                                argument = "duckprob"
                                value = text.split()[1]
                                if value.isdigit():
                                    value = int(value)                    
                                    if 1 <= value <= 99:
                                        send_message("set {0} to {1}".format(argument, value), chat)
                                        db.set(chat, argument, value)
                                        logger(chat,"setting","Set duckprob {0}".format(value))  
                                else:
                                    send_message("{0} is not a valid setting. it must be a number between 1 and 99.".format(value), chat)
                            else:
                                send_message("Missing/wrong argument. Usage: /duckprob <number>", chat)
                        else:
                            send_message("You do not have permission to use this command. You are: {0}.".format(userlevel), chat)
#ducktime                                
                    elif text.startswith("/ducktime"):
                        if userlevel in ["administrator","creator"]:
                            if  (len(text.split())) == 1:
                                got = db.get(chat, "ducktime")
                                got = str(got[0])
                                send_message(got, chat)
                            elif  (len(text.split())) == 2:
                                argument = "ducktime"
                                value = text.split()[1]
                                if value.isdigit():
                                    value = int(value)                    
                                    if 1 <= value <= 360:
                                        send_message("set {0} to {1}".format(argument, value), chat)
                                        db.set(chat, argument, value)
                                        setnextroll(chat)
                                        logger(chat,"setting","Set ducktime {0}".format(value))  
                                else:
                                    send_message("{0} is not a valid setting. it must be a number between 1 and 360.".format(value), chat)
                            else:
                                send_message("Missing/wrong argument. Usage: /ducktime <number>", chat)
                        else:
                            send_message("You do not have permission to use this command. You are: {0}.".format(userlevel), chat)
                    
 #duckwaittime                                
                    elif text.startswith("/duckwaittime"):
                        if userlevel in ["administrator","creator"]:
                            if  (len(text.split())) == 1:
                                got = db.get(chat, "duckwaittime")
                                got = str(got[0])
                                send_message(got, chat)
                            elif  (len(text.split())) == 2:
                                argument = "duckwaittime"
                                value = text.split()[1]
                                if value.isdigit():
                                    value = int(value)                    
                                    if 1 <= value <= 360:
                                        send_message("set {0} to {1}".format(argument, value), chat)
                                        db.set(chat, argument, value)
                                        setnextroll(chat)
                                        logger(chat,"setting","Set duckwaittime {0}".format(value))  
                                else:
                                    send_message("{0} is not a valid setting. it must be a number between 1 and 360.".format(value), chat)
                            else:
                                send_message("Missing/wrong argument. Usage: /duckwaittime <number>", chat)
                        else:
                            send_message("You do not have permission to use this command. You are: {0}.".format(userlevel), chat)
                    
                   
                    elif text.startswith("/scoreset"):
                        if userlevel in ["administrator","creator"]:
                            if  (len(text.split())) == 2:
                                who = text.split()[1]
                                value = text.split()[2]
                                if value.isdigit():
                                    value = int(value)
                                    db.scoreset(chat, who, value)

                    
############ these are bot owner only                            
                if user == 139468375:
                    if chat == -185877423:
                        if text.startswith("/set "):
                            if  (len(text.split())) == 4:
                                chatnum = text.split()[1]
                                if chatnum.startswith('#chat'):
                                    chatnum = chatnum.replace('#chat', '-')
                                if not chatnum.startswith('-'):
                                    chatnum = "-" + chatnum
                                argument = text.split()[2]
                                value = text.split()[3]
                                if chatnum.lstrip("-").isdigit():
                                    validchat = db.newchat(chatnum)
                                    valid = [1]
                                    if validchat == valid:
                                        if argument in ["duckdeployed","duckenabled","logging","init","setting","roll","shots","newuser","timer"]:
                                            #booleans
                                            if value == "true":
                                                send_message("set {0} to {1} for {2}".format(argument, value, chatnum), chat)
                                                db.set(chatnum, argument, value)
                                            elif value == "false":
                                                send_message("set {0} to {1} for {2}".format(argument, value, chatnum), chat)
                                                db.set(chatnum, argument, value)
                                            else:
                                                send_message("{0} is not a valid value. Must be 'true' or 'false'".format(value), chat)
                                        elif argument in ["duckprob","ducktime","duckwaittime","duckflyaway","nextroll"]:
                                            #integers
                                            if value.isdigit():
                                                value = int(value)
                                                send_message("set {0} to {1} for {2}".format(argument, value, chatnum), chat)
                                                db.set(chatnum, argument, value)
                                                
                                        else:
                                            send_message("{0} is not a valid setting.".format(argument), chat)
                                    else:
                                        send_message("Chat {0} not found.".format(chatnum), chat)
                                else:
                                    send_message("Chat must be a number", chat)
                            else:
                                send_message("Missing argument. Usage: /set <chat> <setting> <value>", chat)
#get        
                        elif text.startswith("/get "):
                            if  (len(text.split())) == 3:
                                chatnum = text.split()[1]
                                if chatnum.startswith('#chat'):
                                    chatnum = chatnum.replace('#chat', '-')
                                if not chatnum.startswith('-'):
                                    chatnum = "-" + chatnum
                                argument = text.split()[2]
                                validchat = db.newchat(chatnum)
                                valid = [1]
                                if validchat == valid:
                                    if argument in ["chat_id","chat_name","duckprob","ducktime","duckwaittime","duckdeployed","duckenabled","duckflyaway","nextroll","logging","init","setting","roll","shots","newuser","timer"]:
                                        value = db.get(chatnum, argument)
                                        send_message("{0} is {1}".format(argument, value), chat)
                                    else:
                                        send_message("{0} is not a valid setting.".format(argument), chat)
                                else:
                                    send_message("Chat {0} not found.".format(chatnum), chat)
                            else:
                                send_message("Missing argument. Usage: /get <setting> <value>", chat)

        except Exception as e:
            print(e)

def score(chat, user, dir):
    score = db.scoreget(chat, "ducktime")
    if dir == "add":
        score = score + 1 
        db.scoreset(chat, user, score)
        return score
    else:
        score = score - 1
        db.scoreset(chat, user, score)
        return score
    
    
def setnextroll(chat):
    db = DBHelper()

    ducktime = db.get(chat, "ducktime")
    ducktime = int(ducktime[0])
    ducktime = ducktime * 60
    next = round(time.time()) + ducktime
    db.set(chat, "nextroll", next)
    
def timer():
    timerran()
    global t
    
    t = threading.Timer(10, timer)
    t.start()
    # if nextroll <= currenttime then call duck_roll
def timerran():
    db = DBHelper()
    chatlist = (db.get_chats())
    for chat in chatlist:
        chatname = str(db.get(chat, "chat_name")[0])
        duckenabled = str(db.get(chat, "duckenabled")[0])
        if duckenabled.lower() == "true":
            duckdeployed = str(db.get(chat, "duckdeployed")[0])
            if duckdeployed.lower() == "false":
                ducktime = db.get(chat, "ducktime")
                ducktime = int(ducktime[0])
                ducktime = ducktime * 60
                nextroll = db.get(chat, "nextroll")
                nextroll = int(nextroll[0])
                currenttime = round(time.time())
                if nextroll <= currenttime:
                    #logger(chat,"timer","No Duck, Roll is scheduled.\nNext: {0}\nTime: {1}".format(nextroll,currenttime))
                    logger(chat,"rogueboner","{2}\nNo Duck, Roll is scheduled.\nNext: {0}\nTime: {1}".format(nextroll,currenttime,chatname))
                    duck_roll(chat)
                    next = currenttime + ducktime
                    db.set(chat, "nextroll", next)
                else:
                    #logger(chat,"timer","No Duck, Roll is NOT scheduled.\nNext: {0}\nTime: {1}".format(nextroll,currenttime))
                    logger(chat,"rogueboner","{2}\nNo Duck, Roll is NOT scheduled.\nNext: {0}\nTime: {1}".format(nextroll,currenttime,chatname))
            else:
                currenttime = round(time.time())
                duckflyaway = db.get(chat, "duckflyaway")
                duckflyaway = int(duckflyaway[0])
                if duckflyaway <= currenttime:
                    #logger(chat,"timer","Duck, flyaway triggered.\nFlyA: {0}\nTime: {1}".format(duckflyaway,currenttime))
                    logger(chat,"rogueboner","{2}\nDuck, flyaway triggered.\nFlyA: {0}\nTime: {1}".format(duckflyaway,currenttime,chatname))
                    db.set(chat, "duckdeployed", False)
                    send_message("The duck flew away!", chat)
                else:
                    #logger(chat,"timer","Duck, flyaway NOT triggered..\nFlyA: {0}\nTime: {1}".format(duckflyaway,currenttime))
                    logger(chat,"rogueboner","{2}\nDuck, flyaway NOT triggered..\nFlyA: {0}\nTime: {1}".format(duckflyaway,currenttime,chatname))

def duck_roll(chat):
    db = DBHelper()
    duckenabled = str(db.get(chat, "duckenabled")[0])
    duckdeployed = str(db.get(chat, "duckdeployed")[0])
    chatname = str(db.get(chat, "chat_name")[0])
    if duckenabled.lower() == "true":
        if duckdeployed.lower() == "false":
            duckprob = int(db.get(chat, "duckprob")[0])
            roll = random.randint(1,100)
            if roll < duckprob:
                db.set(chat, "duckdeployed", True)
                send_message("quack", chat)
                
                currenttime = round(time.time())
                duckwaittime = db.get(chat, "duckwaittime")
                duckwaittime = int(duckwaittime[0])
                duckwaittime = duckwaittime * 60
                duckflyaway = currenttime + duckwaittime
                db.set(chat, "duckflyaway", duckflyaway)
                logger(chat,"roll","Rolled a {0}/{1}and deployed a duck.\n".format(roll,duckprob))
            else:
                logger(chat,"roll","Rolled a {0}/{1} and did not deploy a duck.".format(roll,duckprob))
                setnextroll(chat)
        else:
            logger(chat,"roll","Duck already deployed. Not rolling.")
    else:
        logger(chat,"roll","DH DISABLED. Not rolling.")
def main():
    last_update_id = None
    chatlist = (db.get_chats())
    logger("0","init","Currently joined chats:{0}".format(chatlist))
    timer()
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handlemessages(updates)
        time.sleep(0.5)
if __name__ == '__main__':
    main()