from telegram import MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
from collections import defaultdict

import os
import sys
import logging
import json

class adnyFilter(BaseFilter):
    def filter(self, message):
        return ('--' in message.text or '++' in message.text)

def start(bot, update):
    update.message.reply_text('Hello World!')

def myscore(bot, update):
    username = update.message.from_user.username
    score = db[username]
    update.message.reply_text(
            'Hello {}, your score is {}.'.format(username, score))

def score(bot, update):
    update.message.reply_text('to be written')

def update_score(bot, update):
    for mention in update.message.entities:
        if mention.type == 'mention':
            mention_begin = mention.offset
            mention_end = mention_begin + mention.length

        username = update.message.text[mention_begin+1:mention_end]

        if '--' in update.message.text:
            db[username] -= 1
        else:
            db[username] += 1

        with open('adny-bot-db.json', 'w') as dbfile:
            json.dump(db, dbfile)

        update.message.reply_text(
                '{} is now at a score of {}.'.format(username, db[username]))

if "TELEGRAM_BOT_API_KEY" in os.environ:
    updater = Updater(os.environ.get("TELEGRAM_BOT_API_KEY"))
else:
    sys.exit("Telegram Bot API key not in TELEGRAM_BOT_API_KEY environment variable")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

adny_filter = adnyFilter()
total_filter = (Filters.text & Filters.entity(MessageEntity.MENTION) & adny_filter)
updater.dispatcher.add_handler(MessageHandler(total_filter, update_score))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('myscore', myscore))

dbstr = open('adny-bot-db.json', 'r').read()
db_raw = json.loads(dbstr)
db = defaultdict(int, db_raw)

updater.start_polling()
updater.idle()
