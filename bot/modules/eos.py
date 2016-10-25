from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re

@respond_to('!fit (.*)')
#@listen_to('Can someone help me?')
def fit(message, fit):
    # Message is replied to the sender (prefixed with @user)
    message.reply('Processing fit')

    # Message is sent on the channel
    # message.send('I can help everybody!')