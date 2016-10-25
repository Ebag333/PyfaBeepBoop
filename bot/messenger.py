# -*- coding: utf-8 -*-

import logging
import random

from eos import *
from eos.holder_filter import *

logger = logging.getLogger(__name__)

from os import path, getcwd, chdir

def print_my_path():
    print('cwd:     {}'.format(getcwd()))
    print('__file__:{}'.format(__file__))
    print('abspath: {}'.format(path.abspath(__file__)))

print_my_path()

chdir('..')

print_my_path()


class Messenger(object):
    def __init__(self, slack_clients):
        self.clients = slack_clients
        root_path = getcwd()

        #EOS stuff
        data_handler = JsonDataHandler(root_path+'/json_data')  # Folder with Phobos data dump
        cache_handler = JsonCacheHandler(root_path+'/json_data/eos_tq.json.bz2')
        SourceManager.add('tiamat', data_handler, cache_handler, make_default=True)

        skill_groups = set(row['groupID'] for row in data_handler.get_evegroups() if row['categoryID'] == 16)
        self.skills = set(row['typeID'] for row in data_handler.get_evetypes() if row['groupID'] in skill_groups)

        self.fit = Fit()

    def send_message(self, channel_id, msg):
        # in the case of Group and Private channels, RTM channel payload is a complex dictionary
        if isinstance(channel_id, dict):
            channel_id = channel_id['id']
        logger.debug('Sending msg: %s to channel: %s' % (msg, channel_id))
        channel = self.clients.rtm.server.channels.find(channel_id)
        channel.send_message(msg)

    def write_help_message(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = '{}\n{}\n{}\n{}'.format(
            "I'm your friendly Slack bot written in Python.  I'll *_respond_* to the following commands:",
            "> `hi <@" + bot_uid + ">` - I'll respond with a randomized greeting mentioning your user. :wave:",
            "> `<@" + bot_uid + "> joke` - I'll tell you one of my finest jokes, with a typing pause for effect. :laughing:",
            "> `<@" + bot_uid + "> attachment` - I'll demo a post with an attachment using the Web API. :paperclip:")
        self.send_message(channel_id, txt)

    def write_greeting(self, channel_id, user_id):
        greetings = ['Hi', 'Hello', 'Nice to meet you', 'Howdy', 'Salutations']
        txt = '{}, <@{}>!'.format(random.choice(greetings), user_id)
        self.send_message(channel_id, txt)

    def write_prompt(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = "I'm sorry, I didn't quite understand... Can I help you? (e.g. `<@" + bot_uid + "> help`)"
        self.send_message(channel_id, txt)

    def write_joke(self, channel_id):
        question = "Why did the python cross the road?"
        self.send_message(channel_id, question)
        self.clients.send_user_typing_pause(channel_id)
        answer = "To eat the chicken on the other side! :laughing:"
        self.send_message(channel_id, answer)


    def write_error(self, channel_id, err_msg):
        txt = ":face_with_head_bandage: my maker didn't handle this error very well:\n>```{}```".format(err_msg)
        self.send_message(channel_id, txt)

    def demo_attachment(self, channel_id):
        txt = "Beep Beep Boop is a ridiculously simple hosting platform for your Slackbots."
        attachment = {
            "pretext": "We bring bots to life. :sunglasses: :thumbsup:",
            "title": "Host, deploy and share your bot in seconds.",
            "title_link": "https://beepboophq.com/",
            "text": txt,
            "fallback": txt,
            "image_url": "https://storage.googleapis.com/beepboophq/_assets/bot-1.22f6fb.png",
            "color": "#7CD197",
        }
        self.clients.web.chat.post_message(channel_id, txt, attachments=[attachment], as_user='true')

    def write_fit(self, channel_id, msgtext):
        msg_chunks = msgtext.split()

        answer = False

        try:
            command = str(msg_chunks[2])
        except:
            command = ""
            answer = "No commmand given."

        try:
            itemid = str(msg_chunks[3])

            if not itemid.isnumeric():
                itemid = False
        except:
            itemid = False

        try:
            state = str(msg_chunks[4])
        except:
            state = False

        try:
            ammo = str(msg_chunks[5])
        except:
            ammo = False

        if command == "calc" and not answer:
            self.fit.validate()
            answer = "Fit total HP is: " + str(self.fit.stats.hp["total"])
        elif command == "clear" and not answer:
            pass
        elif command == "ship" and itemid and not answer:
            self.fit = Fit()
            for skill_id in self.skills:
                self.fit.skills.add(Skill(skill_id, level=5))
            self.fit.ship = Ship(itemid)
            self.fit.validate()
            answer = "Added ship: " + str(itemid)
        elif command == "addhigh" and not answer:
            self.fit.modules.high.equip(ModuleHigh(itemid, state=state, charge=Charge(ammo)))
            self.fit.validate()
            answer = "Added high slot: " + str(itemid)
        elif command == "addmid" and not answer:
            self.fit.modules.med.equip(ModuleMed(itemid, state=state))
            self.fit.validate()
            answer = "Added mid slot: " + str(itemid)
        elif command == "addlow" and not answer:
            self.fit.modules.low.equip(ModuleLow(itemid, state=state))
            self.fit.validate()
            answer = "Added mid slot: " + str(itemid)
        elif command == "addrig" and not answer:
            self.fit.rigs.equip(Rig(itemid))
            self.fit.validate()
            answer = "Added rig: " + str(itemid)

        if not answer:
            answer = "Not sure what you're trying to do here. Try again."

        self.send_message(channel_id, answer)
