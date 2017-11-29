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
    mentioned_users = set()
    for mention in update.message.entities:
        if mention.type != 'mention':
            continue
        mention_begin = mention.offset
        mention_end = mention_begin + mention.length

        username = update.message.text[mention_begin+1:mention_end]
        mentioned_users.add(username)

    reply_str = ''
    for user in mentioned_users:
        reply_str += '{} has a score of {}.\n'.format(user, db[user])
    update.message.reply_text(reply_str)

def update_score(bot, update):
    mentioned_users = set()
    for mention in update.message.entities:
        if mention.type != 'mention':
            continue
        mention_begin = mention.offset
        mention_end = mention_begin + mention.length

        username = update.message.text[mention_begin+1:mention_end]

        action = update.message.text[mention_end:]
        action = action.strip()
        action = action[:2]

        if '--' in action:
            db[username] -= 1
            mentioned_users.add(username)
        elif '++' in action:
            db[username] += 1
            mentioned_users.add(username)

    with open('adny-bot-db.json', 'w') as dbfile:
        json.dump(db, dbfile)

    reply_str = ''
    for user in mentioned_users:
        reply_str += '{} now has a score of {}.\n'.format(user, db[user])
    update.message.reply_text(reply_str)

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

dbstr = open('incdec-bot-db.json', 'r').read()
db_raw = json.loads(dbstr)
db = defaultdict(int, db_raw)

updater.start_polling()
updater.idle()
