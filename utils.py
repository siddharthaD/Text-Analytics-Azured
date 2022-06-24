from ast import Try
import requests as req
import os

api_key = os.getenv('AZURE_TEXTANA_KEY',None)
log_key = os.getenv('AZURE_TEXTLOG_KEY',None)

async def call_text_analytics_api(document,  endpoint, headers=None):

    if api_key == None:
        print("Configure key please")
        return {"message":"system error"}

    if headers is None:
        headers = { "Ocp-Apim-Subscription-Key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json" }
    response = req.post("https://educativesidtext.cognitiveservices.azure.com//text/analytics/v3.0/" + endpoint, headers=headers, json=document)
    return response.json()

async def get_key_phrases(document):
    endpoint = 'keyPhrases'
    try:
        api_response = await call_text_analytics_api( document, endpoint=endpoint)
        keyPhrases = api_response["documents"]
        for i in range(len(keyPhrases)):
            document_level_keyphrases = keyPhrases[i]["keyPhrases"]
            print("Document {}: KyePhrases: {}".format(i+1, document_level_keyphrases))
        return keyPhrases
    except KeyError:
        print(document)
        print(api_response)

async def get_sentiment(document):
    try:
        endpoint = 'sentiment'
        api_response = await call_text_analytics_api( document, endpoint=endpoint)
        sentiments = api_response["documents"]
        for i in range(len(sentiments)):
            print("Document {0}: Sentiment: {1} ".format(i + 1, sentiments[i]["sentiment"]))
        return sentiments
    except KeyError:
        print(document)
        print(api_response)