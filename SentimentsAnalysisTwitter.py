import oauth2 as oauth
import urllib2 as urllib
import sys
import json
import re

api_key = "*******************"
api_secret = "****************************************************"
access_token_key = "****************************************************"
access_token_secret = "****************************************"

scores = {}

_debug = 0
oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=api_key, secret=api_secret)
signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"

http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,token=oauth_token,http_method=http_method,http_url=url,parameters=parameters)
  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)
  headers = req.to_header()
  if http_method == "POST":
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)
  response = opener.open(url, encoded_post_data)
  return response

def readSentiments(sentimentFile):
    for line in sentimentFile:
        term, score  = line.split("\t")
        scores[term] = int(score)
    # print scores
    
def calculateSentiment(line,outputFile):
    score=0
    tweet_json = json.loads(line)

    # only accept records with a 'text' field and with english language
    if tweet_json.get('text') and tweet_json.get('lang')=='en':
        tweet_text = tweet_json['text'].encode('utf8').split()
        for word in tweet_text:
            # only read alphanumeric words
            if re.match("^[A-Za-z0-9_-]*$", word):
                score += scores.get(word,0)
        outputFile.write(tweet_json['text'].encode('utf8')+"\t"+str(score)+"\n")
        print score

def main():
  url = "https://stream.twitter.com/1/statuses/sample.json"

  outputFile = open("output.txt", "w")

  sentimentFile = open(sys.argv[1])
  readSentiments(sentimentFile)

  parameters = []
  response = twitterreq(url, "GET", parameters)
  for line in response:
      calculateSentiment(line.strip(),outputFile)


if __name__ == '__main__':
  main()
