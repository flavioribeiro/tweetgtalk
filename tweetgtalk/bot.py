#!/usr/bin/env python
import sleekxmpp
import tweepy

import config

class TweetBot(sleekxmpp.ClientXMPP):
    '''
    Handle XMPP logic
    '''

    def __init__(self, jid, password):
        super(TweetBot, self).__init__(jid, password)
        self.add_event_handler("session_start", self.on_start)
        self.add_event_handler("message", self.on_message)
        
        self.message_handler = MessageHandler(bot=self)

    def on_start(self, event):
        self.sendPresence()

    def on_message(self, msg):
        if msg['type'] == 'chat' and msg['body']:
            self.message_handler.handle(msg)


class MessageHandler(object):
    '''
    Handle incomming messages routing to commands or authentication
    '''

    def __init__(self, bot=None):
        self.bot = bot
        self.manager = TwitterManager()
        self.commands_class = TwitterCommands

    def handle(self, msg):
        body = msg['body'].strip()
        jid = msg.getFrom().jid

        account = self.manager.get_or_create_account(jid)
        if account.verified:
            self.execute_command(account, body)
        else: 
            if account.authenticating:
                if account.verify(body):
                    self.send_message(jid, 'Authentication complete!')
                else:
                    self.send_message(jid, 'Invalid verification code')
            else:
                redirect_url = account.authenticate()
                self.send_message(jid, u'Enter the url bellow and click "Allow"')
                self.send_message(jid, redirect_url)
                self.send_message(jid, u'Enter de verification code:')
    
    def execute_command(self, account, command):
        commands = self.commands_class(account.api)
        
        if command == 'timeline':
            result = commands.home_timeline()
        elif command.startswith('tweet'):
            try:
                _, tweet = command.split(" ", 1)
            except ValueError:
                tweet = ""
            result = commands.update_status(tweet)
        else:
            result = "unkown command"

        self.send_message(account.jid, result)
    
    def send_message(self, jid, msg):
        self.bot.sendMessage(jid, msg)


class TwitterManager(object):
    '''
    Manage the twitter accounts
    '''

    def __init__(self):
        self.accounts = {}
    
    def get_account(self, jid):
        try:
            return self.accounts[jid]
        except KeyError:
            return None

    def get_or_create_account(self, jid):
        account = self.get_account(jid)
        if not account:
            account = TwitterAccount(jid)
            self.accounts[jid] = account
        return account


class TwitterAccount(object):
    '''
    Handles a twitter account for an user (JID) and control the authentication
    '''
    def __init__(self, jid):
        self.jid = jid
        self.verified = False
        self.authenticating = False
        self._auth = None
        self.api = None

    def authenticate(self):
        self._auth = tweepy.OAuthHandler(
                config.TWEET_APP_CONSUMER_TOKEN,
                config.TWEET_APP_CONSUMER_SECRET)
        url = self._auth.get_authorization_url()
        self.authenticating = True
        return url

    
    def verify(self, code):
        try:
            self._auth.get_access_token(code)
        except tweepy.error.TweepError:
            self.verified = False
            self.authenticating = True
            return False
        self.api = tweepy.API(self._auth)
        self.authenticating = False
        self.verified = True
        return True


class TwitterCommands(object):
    '''
    Calls commands on API object and returns already formated to answer the user
    '''

    def __init__(self, api):
        self.api = api

    def home_timeline(self):
        status_list = self.api.home_timeline()
        result = []
        tweet = u"@{0}: {1}"
        for status in status_list:
            result.append(tweet.format(status.author.name, status.text))
        
        return u"\n\n".join(result)
    
    def update_status(self, tweet):
        tweet = tweet.strip()
        
        if not tweet:
            return u"Empty tweet"
        
        if len(tweet) > 140:
            return u"Tweet too long, {0} characters. Must be up to 140.".format(len(tweet))
        self.api.update_status(tweet)

        return u"Tweet sent"



def main():
    bot = TweetBot(config.BOT_JID, config.BOT_PASSWORD)
    
    bot.registerPlugin('xep_0030')
    bot.registerPlugin('xep_0004')
    bot.registerPlugin('xep_0060')
    bot.registerPlugin('xep_0199')
    
    print("Created bot")
    
    if bot.connect((config.BOT_HOST, config.BOT_PORT)):
        print("Connected")
        bot.process(threaded=False)
        print("\nDone")
    else:
        print("Not connected")



if __name__ == '__main__':
    main()
