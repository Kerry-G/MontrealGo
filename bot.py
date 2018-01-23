import random
import re
from flask import Flask, request
from pymessenger.bot import Bot
from Utils.reddit.reddit import getImage, getNews, getHistorical
from Utils.weather.weather import receiveWeather, receiveWeatherFromLatLon
from Utils.qrwrapper.qrwrapper import QR_Controller
from config import ACCESS_TOKEN, VERIFY_TOKEN
import emoji

# Variables
bot = Bot(ACCESS_TOKEN)

class Bot_Controller:

    recipient_id = ""
    userType = "PHOTOS"
    params = ['', '']
    QR = None
    location = False
    get_started_types = [
            {'buttontitle': 'Local News', 'payload': 'NOUVELLES'},
            {'buttontitle': 'Photo of Montreal', 'payload': 'PHOTOS'},
            {'buttontitle': 'City Weather', 'payload': 'WEATHER'},
            {'buttontitle': 'Historical Info', 'payload': 'HISTORICAL'},
            {'buttontitle': 'Where is?', 'payload': 'WHERE_IS'}
    ]

    city_types = [
            {'buttontitle': 'Montreal', 'payload': 'MONTREAL'},
            {'buttontitle': 'Toronto', 'payload': 'TORONTO'},
            {'buttontitle': 'Ottawa', 'payload': 'OTTAWA'},
            {'buttontitle': 'Quebec', 'payload': 'QUEBEC'},
            {'buttontitle': 'Vancouver', 'payload': 'VANCOUVER'},
            {'content_type': 'location' } 
    ]


    where_is_types = [
            {'buttontitle': 'Mont-Royal', 'payload': 'NOUVELLES'},
            {'buttontitle': 'Vieux-Port', 'payload': 'PHOTOS'},
            {'buttontitle': 'Parc Jean Drapeau', 'payload': 'WEATHER'},
            {'buttontitle': 'Botanical Garden', 'payload': 'HISTORICAL'}
    ]

    def __init__(self):
        self.QR = QR_Controller(self)

    ''' Main request handling when user write to the bot
    '''
    def receive_message(self):
        if request.method == 'GET':
            """Before allowing people to message your bot, Facebook has implemented a verify token
            that confirms all requests that your bot receives came from Facebook."""
            token_sent = request.args.get("hub.verify_token")
            return self.verify_fb_token(token_sent)
        #if the request was not get, it must be POST and we can just proceed with sending a message back to user
        else:
        # get whatever message a user sent the bot
            output = request.get_json()
            print(output)
            for event in output['entry']:

                if "standby" in event:
                    standbyChannel = event["standby"]
                    for standby in standbyChannel:
                        self.recipient_id = standby['sender']['id']
                        payloadtest = standby.get("postback")
                        if payloadtest["title"] == "Get Started":
                            self.userType = "GET_STARTED"
                            self.responseGenerator()

                if "messaging" in event:
                    messaging = event['messaging']
                    for message in messaging:
                        if message.get('message'):
                            #Facebook Messenger ID for user so we know where to send response back to
                            self.recipient_id = message['sender']['id']
                            if message['message'].get('text'):
                                self.figureOutType(message['message'].get('text'))
                                self.responseGenerator()

                            #if user sends us a GIF, photo,video, or any other non-text item
                            if message['message'].get('attachments'):
                                if message['message'].get('attachments')[0].get('payload'):
                                    if message['message'].get('attachments')[0].get('payload').get('coordinates'):
                                        lat = message['message'].get('attachments')[0].get('payload').get('coordinates').get('lat')
                                        lon = message['message'].get('attachments')[0].get('payload').get('coordinates').get('long')
                                        self.QR.send_quick_replies(receiveWeatherFromLatLon(lat, lon), self.get_started_types)
                                    else:
                                        response_sent_nontext = self.get_message()
                                        self.QR.send_quick_replies(response_sent_nontext, self.get_started_types)

        return "Message Processed"
    

    ''' Verifies the Facebook token
    '''
    def verify_fb_token(self, token_sent):
        #take token sent by facebook and verify it matches the verify token you sent
        #if they match, allow the request, else return an error
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return 'Invalid verification token'


    '''chooses a random message to send to the user
    '''
    def get_message(self):
        sample_responses = ["Welcome to MontrealGo Alpha " + emoji.emojize(':grinning:', use_aliases=True), emoji.emojize(':thumbsup:', use_aliases=True), "Hi! " + emoji.emojize(':blush:', use_aliases=True)]
        
        # return selected item to the user
        return random.choice(sample_responses)


    '''uses PyMessenger to send response to user
    '''
    def send_message(self, recipient_id, response):
        #sends user the text message provided via input response parameter
        bot.send_text_message(recipient_id, response)
        return "success"

    ''' Triggers the proper data message Type
    '''
    def responseGenerator(self):
        messageType = self.userType
        if messageType is "GET_STARTED":
            self.QR.send_quick_replies(self.answerSelector(messageType), self.get_started_types)
        elif messageType is "NOUVELLES":
            news = getNews()

            elements = []
            element = {"title": news['title'], "subtitle": "MessengerGo",  "item_url": news['url'] }
            elements.append(element)
            bot.send_generic_message(self.recipient_id, elements)
            self.QR.send_quick_replies("What else would you like to do?", self.get_started_types)
        elif messageType is "PHOTOS":
            image = getImage()
            bot.send_image_url(self.recipient_id, image['url'])
            self.QR.send_quick_replies(self.answerSelector(messageType) + "by /u/" + str(image['author']), self.get_started_types)
        elif messageType is "STM":
            pass
        elif messageType is "WEATHER":
            self.send_message(self.recipient_id,receiveWeather(self.params[0]))
            self.QR.send_quick_replies("Would you like the weather for another city?", self.city_types)
        elif messageType is "HISTORICAL":
            historical = getHistorical()
            self.send_message(self.recipient_id, self.answerSelector(messageType))
            self.QR.send_quick_replies(historical['title'] + ' ' + historical['url'], self.get_started_types)
        elif messageType is "ERROR":
            self.send_message(self.recipient_id, emoji.emojize(':laughing:', use_aliases=True) + " " + self.answerSelector(messageType) )
            self.QR.send_quick_replies("Here is what I can help you with.", self.get_started_types)
        elif messageType is "WHERE_IS_FIRST":
            self.QR.send_quick_replies("Where would you like to go?", self.where_is_types)
        elif messageType is "WHERE_IS":
            where_is_urls = {'Mont-Royal': 'https://goo.gl/maps/cUYD8V6wvo42',
            'Vieux-Port': 'https://goo.gl/maps/xtYmjghFsqn',
            'Parc Jean Drapeau': 'https://goo.gl/maps/MsTsEPTpuSu',
            'Botanical Garden': 'https://goo.gl/maps/Cnm8tLcAYAF2'}
            elements = []
            element = {"title": self.location, "subtitle": "Montreal Tourism",  "item_url": where_is_urls[self.location] }
            elements.append(element)
            bot.send_generic_message(self.recipient_id, elements)
            self.send_message(self.recipient_id, "I hope you have fun there!")
            self.QR.send_quick_replies("What else can I do for you?", self.get_started_types)
        else:
            self.send_message(self.recipient_id, ':)')

    def figureOutType(self, a):
        if self.iequal(a,"get started") or self.iequal(a,"hey") or self.iequal(a,"hi") or self.iequal(a,"salut") or self.iequal(a,"bonjour"):
            self.userType = "GET_STARTED"
        elif self.iequal(a,"News") or self.iequal(a,"Nouvelles") or self.iequal(a,"Local News"):
            self.userType = "NOUVELLES"
        elif self.iequal(a,"Where is?") or self.iequal(a,'Where is') or self.iequal(a,'where'):
            self.userType = "WHERE_IS_FIRST"
        elif self.iequal(a,"Weather") or self.iequal(a,"meteo") or self.iequal(a,"City Weather"):
            self.userType="WEATHER"
            self.params=["montreal"]
        elif self.iequal(a, "Montreal"):
            self.userType = "WEATHER"
            self.params = ["montreal"]
        elif self.iequal(a,"Mont-Royal"):
            self.location = "Mont-Royal"
            self.userType = "WHERE_IS"
        elif self.iequal(a,"Vieux-Port"):
            self.location = "Vieux-Port"
            self.userType = "WHERE_IS" 
        elif self.iequal(a,"Parc Jean Drapeau"):
            self.location = "Parc Jean Drapeau"
            self.userType = "WHERE_IS"   
        elif self.iequal(a,"Botanical Garden"):
            self.location = "Botanical Garden"
            self.userType = "WHERE_IS"
        elif self.iequal(a,"Ottawa"):
            self.userType="WEATHER"
            self.params=["ottawa"]
        elif self.iequal(a,"Vancouver"):
            self.userType="WEATHER"
            self.params=["Vancouver"]
        elif self.iequal(a,"Toronto"):
            self.userType="WEATHER"
            self.params=["Toronto"]
        elif self.iequal(a,"Halifax"):
            self.userType="WEATHER"
            self.params=["Halifax"]
        elif self.iequal(a, "HISTORICAL") or self.iequal(a, "Historical Info"):
            self.userType = "HISTORICAL"
        elif self.iequal(a, "STM"):
            self.userType = "STM"
        elif self.iequal(a, "PHOTOS") or self.iequal(a, "picture") \
                or self.iequal(a, "PHOTO") or self.iequal(a, "pictures") or self.iequal(a, "Photo of Montreal"):
            self.userType = "PHOTOS"
        elif self.internationalBoolean(a):
            self.userType = "WEATHER"
            self.params = [self.internationalFinder(a)]
        else :
            self.userType = "ERROR"

    def iequal(self, a, b):
        try:
            return a.upper() == b.upper()
        except AttributeError:
            return a == b

    def internationalBoolean(self, userWeather):
        x=[]
        x=(re.split(r' (\s*)', userWeather))
      
        if self.iequal(x[0],'weather'):
            return True

    def internationalFinder(self, userWeather):
        x=[]
        x=(re.split(r' (\s*)', userWeather))
        if self.iequal(x[0],'weather'):
            return x[2]


    def answerSelector(self,userValue):
        if(userValue == "GET_STARTED"): 
            selectable = ['Hi, I am MontrealGo! What can I help you with', 'Hey, I am MontrealGo! Is there something you need help with?']
            return selectable[random.randrange(0,len(selectable),1)]

        elif(userValue == "NOUVELLES"): 
            selectable = ['Here\'s some local Montreal news. ', 'Stay updated with local montreal news.']
            return selectable[random.randrange(0,len(selectable),1)]

        elif(userValue == "PHOTOS"):
            selectable2 = ['Enjoy the following Montreal image by ', 'Here is a photo of Montreal by ']
            return selectable2[random.randrange(0,len(selectable2),1)]
        

        elif(userValue == "HISTORICAL"):
            selectable3 = ['Montreal is a very historical place. Here is some information about it.', 'Montreal has a very rich history, here is part of it']
            return selectable3[random.randrange(0,len(selectable3),1)]
        
        else:
            selectable4 = ['I did not understand that command.', 'Sorry try again my friend, this did not compute.', "Oops, I could not understand that."]
            return selectable4[random.randrange(0,len(selectable4),1)]