import requests
import tweepy
import yaml
import hashlib
import sys
import os
from bs4 import BeautifulSoup

def prepareHashtag(string): 
    return "#" + string.replace(" ", "").replace(".", "")

def sendTweet(tweet):
    env = yaml.safe_load(open("env.yaml", "r"))
    consumer_key = env['TWITTER']['API_KEY']
    consumer_secret = env['TWITTER']['API_KEY_SECRET']
    access_token = env['TWITTER']['ACCESS_TOKEN']
    access_token_secret = env['TWITTER']['ACCESS_TOKEN_SECRET']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    api.update_status(tweet)

def scrap(lastHash):
    tweets = []
    newHash = ""
    pageUrl = "http://biznes.pap.pl/pl/reports/espi/all,0,0,0,1"
    page = requests.get(pageUrl)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(class_="espi")
    rows = table.find_all(class_="inf")

    today = table.find(class_='dni').text.strip()

    for row in rows:
        link = row.find("a", class_="th")
        title = link.text.strip().replace("???", "")
        url = link.get("href")
        cols = row.find_all("td")
        time = cols[0].text.strip()
        number = cols[1].text.strip()
        company = cols[2].text.strip()

        hashtags = '#espi #gpw #NewConnect #giełda #inwestowanie ' + prepareHashtag(company)

        tweet =  company + ' (' + number + '): ' + title + ' ' + url + ' [' + today + ' ' + time + '] ' + hashtags
        
        hash = hashlib.md5(tweet.encode('utf-8')).hexdigest()
        # print(hash)
        # print(lastHash)
        # print(newHash)
        if (hash != lastHash):
            tweets.append(tweet)
            if (newHash == ""):
                newHash = hash
    
    if (newHash != ""):
        saveLastHash(newHash)
    
    tweets.reverse()
    return tweets

def getLastHash():
    hash = ""
    hashFile = "lastHash.txt"
    try:
        hashdocument = open(hashFile, "r")
    except IOError:
        print("Invalid file.")
        sys.exit()
    else:
        hash = hashdocument.readline()
        hash = hash.replace("\n", "")
    return hash

def saveLastHash(hash):
    hashFile = "lastHash.txt"
    try:
        hashdocument = open(hashFile, "w")
    except IOError:
        print("Invalid file.")
        sys.exit()
    else:
        hashdocument.write(hash)
        hashdocument.close()

# get last hash from file
lastHash = getLastHash()

# start scraping
tweets = scrap(lastHash)

if len(tweets) > 0:
    for tweet in tweets:
        print(tweet)
        print('--------------------------------------------------')
        sendTweet(tweet)
else:
    print('No tweets to post.')