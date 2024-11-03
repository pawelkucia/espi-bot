import requests
import tweepy
import yaml
import hashlib
import sys
import os
from bs4 import BeautifulSoup

def prepareHashtag(company_name): 
    return "#" + company_name.replace(" ", "").replace(".", "").replace("&", "")

def sendTweet(tweet):
    env = yaml.safe_load(open("env.yaml", "r"))
    consumer_key = env['TWITTER']['API_KEY']
    consumer_secret = env['TWITTER']['API_KEY_SECRET']
    access_token = env['TWITTER']['ACCESS_TOKEN']
    access_token_secret = env['TWITTER']['ACCESS_TOKEN_SECRET']

    try:
        # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        # auth.set_access_token(access_token, access_token_secret)
        # api = tweepy.API(auth)
        # api.update_status(tweet)

        client = tweepy.Client(consumer_key=consumer_key, 
                                consumer_secret=consumer_secret,
                                access_token=access_token, 
                                access_token_secret=access_token_secret)
        client.get_me()
        client.create_tweet(text=tweet)
    except tweepy.errors.TweepyException as e:
        print(e)
    else:
        print('Post OK')

def scrap(lastHash):
    tweets = []
    newHash = ""
    tweetsDone = False
    #pageUrl = "http://biznes.pap.pl/pl/reports/espi/all,0,0,0,1"
    pageUrl = "https://espiebi.pap.pl"
    page = requests.get(pageUrl)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(class_="newsList")
    rows = table.find_all(class_="news")

    for row in rows:
        if not tweetsDone:
            link = row.find("a", class_="link")
            title = link.text.strip()
            title_splitted = title.split(' - ')
            company_name = title_splitted[0].strip()
            content = title_splitted[1].strip()
            url = link.get("href")
            cols = row.find_all("div")
            newsType = cols[0].text.strip()
            time = cols[1].text.strip()
            number = cols[2].text.strip()
            number = number.replace("Raport Bieżący nr ", "").replace("Raport bieżący nr ", "")
            number = number.replace(" ", "")
            
            if (len(content) > 200):
                content = content[:200] + '...'

            hashtags = '#' + newsType + ' #gpw #giełda #inwestowanie ' + prepareHashtag(company_name)

            tweet =  company_name + ' (' + newsType + ' ' + time + ' ' + number + '): ' + content + ' ' + pageUrl + url + ' ' + hashtags
            
            hash = hashlib.md5(tweet.encode('utf-8')).hexdigest()
            # print(hash)
            # print(lastHash)
            # print(newHash)
            if (hash != lastHash):
                tweets.append(tweet)
                #if (newHash == ""):
                newHash = hash
            else:
                tweetsDone = True
    
    if (newHash != ""):
        saveLastHash(newHash)
        print('LastHash saved: ' + newHash)
    
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
    tweet = tweets[0]
    #for tweet in tweets:
    print(tweet)
    # print(len(tweet))
    sendTweet(tweet)
    print('--------------------------------------------------')
        
else:
    print('No tweets to post.')