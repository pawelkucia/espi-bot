import requests
import tweepy
from bs4 import BeautifulSoup

def prepareHashtag(string): 
    return "#" + string.replace(" ", "").replace(".", "")

def sendTweet(tweet):
    consumer_key = "#"
    consumer_secret = "#"
    access_token = "#"
    access_token_secret = "#"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    api.update_status(tweet)

def scrap():
    page = requests.get("http://biznes.pap.pl/pl/reports/espi/all,0,0,0,1")
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(class_="espi")
    rows = table.find_all(class_="inf")

    today = table.find(class_='dni').text.strip()

    for row in rows:
        link = row.find("a", class_="th")
        title = link.text.strip()
        url = link.get("href")
        cols = row.find_all("td")
        time = cols[0].text.strip()
        number = cols[1].text.strip()
        company = cols[2].text.strip()

        hashtags = '#espi ' + prepareHashtag(company)

        tweet = '[' + today + ' ' + time + '] ' + number + ' ' + company + ' - ' + title + ' ' + url + ' ' + hashtags
        
        print(tweet)
        print('--------------------------------------------------')
        sendTweet(tweet)

scrap()