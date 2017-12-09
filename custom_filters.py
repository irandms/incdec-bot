from telegram.ext import BaseFilter

class IncDecFilter(BaseFilter):
    def filter(self, message):
        actions = ['--', '++', '—']
        return any(action in message.text for action in actions)
