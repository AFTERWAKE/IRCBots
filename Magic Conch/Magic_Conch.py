from botlib import Bot, Group, Trigger
import json

def start_bot(item):
    bot = Bot(item['server'], item['channel'], item['nick'], item['ident'])
    for trigger in item['triggers']:
        groups = []
        regex = trigger['pattern']
        if 'isCommand' not in trigger:
            trigger['isCommand'] = False
        for key, value in trigger.items():
            if key in ('responses', 'pattern', 'isAction', 'isCommand'):
                continue
            groups.append(Group(key, *value))
        bot.add_trigger(Trigger(regex, trigger['responses'], trigger['isAction'], trigger['isCommand'], *groups))
    return bot


def main():
    with open(r'Magic_Conch.json') as f:
        config = json.load(f)
    bot = start_bot(config)
    bot.act()

main()
