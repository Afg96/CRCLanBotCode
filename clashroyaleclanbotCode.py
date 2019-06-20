import json 
import requests
import time
import urllib
import datetime

TOKEN = "TOKENHERE" #Telegram token here
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=600"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates, text):
    for update in updates["result"]:
        try:
            #text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            if "BOT GIVE UPDATE".lower() in str(update["message"]).lower():
                send_message(text, chat)
        except Exception as e:
            print(e)
            

def send_message(text, chat_id):
    url = URL + "sendMessage"
    response_content = post_sendMessage(url, chat_id, text)
    print(response_content)
    #URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)

    
def post_sendMessage(url, chat_id, text):
    response = requests.post(url,  data={'chat_id': chat_id, 'text': text})
    content = response.content.decode("utf8")
    return content

def player_sort(player):
    value = player[0][-1][3:]
    if not value:
        return 0
    return value
    
    
def clan_stats(updates):
    r=requests.get("https://v3-beta.royaleapi.com/clan/CLANTAG", headers={"Accept":"application/json", 
    "authorization":"Bearer TOKENHERE"}) #CR API TOKEN
    clan = r.json()
    
    s=requests.get("https://v3-beta.royaleapi.com/clan/CLANTAG/warlog", headers={"Accept":"application/json", 
    "authorization":"Bearer TOKENHERE"}) #CR API TOKEN
	warLog = s.json()[:5]
    
    players = {}
    date = [""]*21
    column = [""]*21
    column[0] = "Name"
    
    temp = 5
    i = 4     
    
    for b in warLog:
      #print(b)
      time = b["warEndTime"][:10]
      time = datetime.datetime.strptime(time, '%Y-%m-%d')
      time = datetime.datetime.strftime(time, '%d.%m.%y')
      
      date[i*4+1] = time
      
      column[i*4+1] = "Karten_" + str(temp)
      column[i*4+2] = "Sammelkämpfe_" + str(temp)
      column[i*4+3] = "Finalkämpfe_" + str(temp)
      column[i*4+4] = "Siege_" + str(temp)
      temp = temp - 1
      
      p = b["participants"]
      for j in p:
        if j["tag"] not in players:
          players[j["tag"]] = [j["name"]] + [""]*16
          for m in clan["members"]:
            if j["tag"] == m["tag"]:
                don = m.get('donations')
                players[j["tag"]][16] = f"D: {don}"
        
        players[j["tag"]][i*3+1] = f"SK{i+1} : {j['collectionDayBattlesPlayed']}"
        players[j["tag"]][i*3+2] = f"FK: {j['battlesPlayed']}"
        players[j["tag"]][i*3+3] = f"W: {j['wins']}"
        
        if players[j["tag"]][16] == "" or players[j["tag"]][16] == " ":
            players[j["tag"]][16] = "D: 0"
       
      i -= 1
        
    pList = sorted(players.items(), key=lambda x: int(x[1][-1][3:]), reverse=True)
    
    with open("clankrieg.csv","w") as file:
     file.write(str(column))
     file.write("\n")
     file.write(str(date))
     file.write("\n")
     
     final = ""
     count = 0
     rest = 0

     for l in pList:
         temp = "\n" + str(l[1]).strip() + "\n"
         temp = temp.split("D: ")[0] + "\n"
         file.write(temp)
         file.write("\n")
         temp = temp.replace("'", "")
         temp = temp.replace("[", "")
         temp = temp.replace(", ]", "")
         temp = temp.replace("]", "")
         temp = temp.replace("SK", "\nSK")
         temp = temp.replace(",", "")
         final += temp
         count += 1
         rest += 1
         
         if count is 25:
             echo_all(updates, final)
             final = ""
             count = 0
             rest = 0
     if rest > 1:
             echo_all(updates, final)
 
 
def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            clan_stats(updates)


if __name__ == "__main__":
    main()