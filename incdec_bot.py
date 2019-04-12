from telegram import MessageEntity
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from collections import defaultdict
from rotate_word import rotate_word
from mention_subgroup import mention_subgroup

from config import ROTATE_MAX_CHARS, SUBGROUPS
from secrets import TELEGRAM_BOT_API_KEY

import os
import sys
import logging
import json
from custom_filters import IncDecFilter

def start(bot, update):
    update.message.reply_text('Hello World!')

"""
Replies with a rotated meme string, courtesy of @inityx, of the message
which trigger this handler.
"""
def rotate(bot, update, args):
    text_to_rotate = ' '.join(args)
    if len(text_to_rotate) > ROTATE_MAX_CHARS:
        update.message.reply_text("Message was too long. Please limit your " \
                "rotations to {} characters or less.".format(ROTATE_MAX_CHARS))
        return
    reply_str = "```\n"
    reply_str += rotate_word(text_to_rotate)
    reply_str += "```"
    update.message.reply_text(reply_str, parse_mode=ParseMode.MARKDOWN)
    
"""
Replies with a message mentioning all people in a related subgroup.
"""
def mention(bot, update, args):
    sender = update.message.from_user.username
    reply_str = mention_subgroup(args, sender, SUBGROUPS)
    update.message.reply_text(reply_str, parse_mode=ParseMode.MARKDOWN)

"""
Replies with the score of the user whom'st'dve triggers this handler.
"""
def myscore(bot, update):
    username = update.message.from_user.username
    score = db[username]
    update.message.reply_text(
            'Hello {}, your score is {}.'.format(username, score))

"""
Replies with the score of all the mentioned targets in the message text.
"""
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


"""
Leaderboard functionality
"""
def leaderboard(bot, update):
    results = sorted(db.items(), key=lambda entry: entry[1])
    if len(results) < 5:
        top = results
        bottom = results
    else:
        top = results[len(results)-5:]
        top = top[::-1]
        bottom = results[:5]

    reply_str = 'Top 5 scores:\n'
    for entry in top:
        reply_str += "{}: {}\n".format(entry[0], entry[1])
    reply_str += '\nBottom 5 scores:\n'
    for entry in bottom:
        reply_str += "{}: {}\n".format(entry[0], entry[1])

    update.message.reply_text(reply_str)


"""
Updates the score of all mentioned targets based off the action string
immediately following the mention.
"""
def update_score(bot, update):
    mentioned_users = set()
    for mention in update.message.entities:
        mention_begin = mention.offset
        mention_end = mention_begin + mention.length

        # add one to the start to cut the '@' character
        username = update.message.text[mention_begin+1:mention_end]

        # Prevent users from modifying their own score
        if username == update.message.from_user.username:
            continue

        # Extract the action from the message
        action = update.message.text[mention_end:].strip()[:2]

        if '--' in action or '—' in action:
            if username == 'irandms':
                db[username] += 1
            else:
                db[username] -= 1
            mentioned_users.add(username)
        elif '++' in action:
            db[username] += 1
            mentioned_users.add(username)

    with open('incdec-bot-db.json', 'w') as dbfile:
        json.dump(db, dbfile)

    reply_str = ''
    for user in mentioned_users:
        reply_str += '{} now has a score of {}.\n'.format(user, db[user])
    update.message.reply_text(reply_str)

"""
Respond with a link to the provided subreddit
"""
def subreddit(bot, update, args):
    if len(args) == 0:
        update.message.reply_text("You forgot the subreddit, idiot")
        return
    
    update.message.reply_text("https://old.reddit.com/r/{}".format(args[0]))

# MAIN PROGRAM
if __name__ == '__main__':
    updater = Updater(TELEGRAM_BOT_API_KEY)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    custom_filter = IncDecFilter()
    total_filter = (Filters.text & Filters.entity(MessageEntity.MENTION) & custom_filter)

    updater.dispatcher.add_handler(MessageHandler(total_filter, update_score))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('rotate', rotate, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('mention', mention, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('score', score))
    updater.dispatcher.add_handler(CommandHandler('myscore', myscore))
    updater.dispatcher.add_handler(CommandHandler('leaderboard', leaderboard))
    updater.dispatcher.add_handler(CommandHandler('r', subreddit, pass_args=True))

    dbstr = open('incdec-bot-db.json', 'r').read()
    db_raw = json.loads(dbstr)
    db = defaultdict(int, db_raw)

    updater.start_polling()
    updater.idle()
