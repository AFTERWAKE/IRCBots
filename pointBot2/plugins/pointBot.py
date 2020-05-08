"""
A plugin for sopel bot that runs a game called pointBot
By: Jason Logerquist
"""
from sopel import module, tools
from datetime import datetime

pluginName = "pointBot"

startHour = 8
stopHour = 17

ptsExpr = r"^(\+|-)(\d+)\s(?:to\s)?(\w+).*$"

def setup(bot):
    updateGameRunning(bot)
    pass

def updateGameRunning(bot):
    """
    Gets game state and last hour from db to determine whether to change game state
    """
    currentHour = datetime.now().hour
    workhour = currentHour >= startHour and currentHour < stopHour

    setGameRunning(bot.db, pluginName, workhour)



@module.interval(300)
def checkGameRunning(bot):
    """
    Check every 5 mins for gamerunning state
    """
    updateGameRunning(bot)


@module.rule(ptsExpr)
def addGPoints(bot, trigger):
    """
    Regex that catches increment and decrement of user pts
    """
    if not trigger.is_privmsg:
        gameRunning = getGameRunning(bot.db, trigger.sender)
        if not gameRunning:
            bot.reply("The game is not running right now")
            return
        groups = trigger.groups()
        points = int(groups[1])
        if groups[0] == '-':
            amount = -points
        else:
            amount = points

        user = groups[len(groups)-1]

        if user == trigger.nick:
            bot.reply("YOU CAN'T GIVE YOURSELF POINTS!!!")
            return

        players = getPlayers(bot.db, bot.users)
        buser = user in players
        if not buser:
            bot.say("Invalid player", trigger.nick)
            return

        checkPlayerReset(bot.db, trigger.nick)
        gpts = getgpts(bot.db, trigger.nick)
        if points > gpts:
            bot.say("You don't have enough gift points", trigger.nick)
            return

        addpts(bot.db, user, amount)
        addgpts(bot.db, trigger.nick, -points)


@module.nickname_commands(r'help')
def help(bot, trigger):
    """
    pointBot help command
    """
    print("Admin Commands: start, stop, auto, reset, save, restore, say <msg>, me <action>, msg <nick> <msg>, status <user>, setpts <user/all> <points>, setgp <user/all> <gp>, ignore <user>, unignore <user>")
    bot.say("User Commands: help, rules, points, [e.g. pointBot, help]. PM anything for your status.")
    bot.say("Point Exchanges: +/-<pts> [to] <user> [reason] (e.g. +1 to user for being awesome)")


@module.nickname_commands(r'rules')
def rules(bot, trigger):
    """
    pointBot rules command
    """
    bot.say("Hello, it's me, pointBot. I keep track of +s and -s handed out in the IRC. You get 10 points to give away every day, and these points are refreshed every morning at 8 AM. Using bots is not allowed. If you run into any issues, talk to the admin (JSON). Have a day.")


@module.require_admin()
@module.nickname_commands(r'adminhelp')
def helpadmincommand(bot, trigger):
    """
    Prints out admin help
    """
    bot.say("Admin Commands: status [<user>], setpts <user/all> <points>, setgpts <user/all> <gpts>, ignore <user>, unignore <user>, setbot <user> <true/false>, setalias <user> <alias> (will use user's pts if both nicks have pts), unalias <alias>", trigger.nick)



@module.nickname_commands(r'points')
def displaypoints(bot, trigger):
    """
    prints out the points scoreboard
    """
    players = getPlayers(bot.db, bot.users)
    ptsstring = displayPoints(bot.db, players)
    bot.say(ptsstring)


@module.require_admin()
@module.nickname_commands(r'reset')
def resetcommand(bot, trigger):
    """
    Reset game for the day. Sets all users' gift points to 10
    """
    bot.say("The game has reset, everyone has 10 gift points now")
    players = getPlayers(bot.db, bot.users)
    resetGame(bot.db, players)


@module.require_admin()
@module.nickname_commands(r'setpts')
def setptscommand(bot, trigger):
    """
    Set one user's or all's point count
    """
    args = trigger.group(2).split()

    try:
        args[1] = int(args[1])
    except ValueError:
        bot.say("Invalid number", trigger.nick)
        return

    buser = getUserFromUsers(args[0], bot.users)
    if buser is not None:
        setpts(bot.db, buser.nick, args[1])
    elif args[0].lower() == "all":
        players = getPlayers(bot.db, bot.users)
        for user in players:
            setpts(bot.db, user, args[1])
    else:
        bot.say("Invalid user option", trigger.nick)


@module.require_admin()
@module.nickname_commands(r'setgpts')
def setgptscommand(bot, trigger):
    """
    Set one user's or all gift point count
    """
    args = trigger.group(2).split()

    try:
        args[1] = int(args[1])
    except ValueError:
        bot.say("Invalid number", trigger.nick)
        return

    buser = getUserFromUsers(args[0], bot.users)
    if buser is not None:
        setgpts(bot.db, buser.nick, args[1])
    elif args[0].lower() == "all":
        players = getPlayers(bot.db, bot.users)
        for user in players:
            setgpts(bot.db, user, args[1])
    else:
        bot.say("Invalid user option", trigger.nick)


@module.require_admin()
@module.nickname_commands(r'setbot')
def setbotcommand(bot, trigger):
    """
    Set a nick's bot status
    """
    args = trigger.group(2).split()
    if len(args) < 2:
        bot.say("Not enough arguments", trigger.nick)
        return
    user = getUserFromUsers(args[0], bot.users)
    isbot = args[1].lower() in ['true', '1', 't', 'y', 'yes']
    if user is not None:
        setUserBotStatus(bot.db, user.nick, str( isbot ))


@module.require_admin()
@module.nickname_commands(r'ignore')
def setignorecommand(bot, trigger):
    """
    Set a nick to ignore status
    """
    args = trigger.group(2).split()
    if len(args) < 1:
        bot.say("User not specified", trigger.nick)
        return
    user = getUserFromUsers(args[0], bot.users)
    if user is not None:
        setUserIgnoreStatus(bot.db, user.nick, "True")


@module.require_admin()
@module.nickname_commands(r'unignore')
def setunignorecommand(bot, trigger):
    """
    Set a nick to unignore status
    """
    args = trigger.group(2).split()
    if len(args) < 1:
        bot.say("User not specified", trigger.nick)
        return
    user = getUserFromUsers(args[0], bot.users)
    if user is not None:
        setUserIgnoreStatus(bot.db, user.nick, "False")


@module.nickname_commands(r'status')
def statuscommand(bot, trigger):
    """
    Get status of user or other user if admin
    """
    if getUserIgnoreStatus(bot.db, trigger.nick) == "True":
        return
    if trigger.group(2) is None or not trigger.admin:
        checkPlayerReset(bot.db, trigger.nick)
        userpts = getpts(bot.db, trigger.nick)
        usergpts = getgpts(bot.db, trigger.nick)
        bot.say("You have {} points and {} gift points left".format(userpts, usergpts), trigger.nick)
    else:
        args = trigger.group(2).split()
        user = args[0]
        players = getPlayers(bot.db, bot.users)
        if user not in players:
            bot.reply("Invalid user")
        else:
            checkPlayerReset(bot.db, user)
            userpts = getpts(bot.db, user)
            usergpts = getgpts(bot.db, user)
            bot.say("{} has {} points and {} gift points left".format(user, userpts, usergpts), trigger.nick)


@module.require_admin()
@module.nickname_commands(r'setalias')
def aliasnickcommand(bot, trigger):
    """
    Set an alias for a nick
    """
    args = trigger.group(2).split()
    if len(args) < 2:
        bot.say("Not enough arguments", trigger.nick)
        return
    aliasNick(bot.db, args[0], args[1])


@module.require_admin()
@module.nickname_commands(r'unalias')
def unaliascommand(bot, trigger):
    """
    Unalias a nick
    """
    args = trigger.group(2).split()
    if len(args) < 1:
        bot.say("Nick not supplied", trigger.nick)
        return
    unaliasNick(bot.db, args[0])


"""
DB helper functions
"""
def displayPoints(db, users):
    returnString = "Here is a list of points in the format 'User: Total Points' "
    ptslist = []
    for user in users:
        pts = getpts(db, user)
        ptslist.append((pts, "|{}|: {}, ".format(user, pts)))
        print(user, "gpts:", getgpts(db, user))
    ptslist.sort(reverse=True)
    for row in ptslist:
        returnString += row[1]
    return returnString[:-2]


def resetGame(db, users):
    for user in users:
        db.set_nick_value(user,"gpts", 10)


def getpts(db, user):
    return db.get_nick_value(user, "pts", 0)


def setpts(db, user, pts):
    db.set_nick_value(user, "pts", pts)


def addpts(db, user, pts):
    cpts = getpts(db, user)
    setpts(db, user, pts+cpts)


def getgpts(db, user):
    return db.get_nick_value(user, "gpts", 0)


def setgpts(db, user, gpts):
    db.set_nick_value(user, "gpts", gpts)


def addgpts(db, user, gpts):
    cgpts = getgpts(db, user)
    setgpts(db, user, gpts+cgpts)


def getGameRunning(db, plugin):
    return db.get_plugin_value(plugin, "gamerunning", False)


def setGameRunning(db, plugin, value):
    db.set_plugin_value(plugin, "gamerunning", value)


def getLastHour(db, plugin):
    return db.get_plugin_value(plugin, "lasthour", 0)


def setLastHour(db, plugin, value):
    db.set_plugin_value(plugin, "lasthour", value)


def getUserFromUsers(nick, users):
    return users.get(tools.Identifier(nick))


def getUserBotStatus(db, user):
    return db.get_nick_value(user, "bot", "False")


def setUserBotStatus(db, user, status):
    db.set_nick_value(user, "bot", status)


def getUserIgnoreStatus(db, user):
    return db.get_nick_value(user, "ignore", "False")


def setUserIgnoreStatus(db, user, status):
    db.set_nick_value(user, "ignore", status)


def getPlayers(db, users):
    players = []
    for user in users:
        isbot = getUserBotStatus(db, user) == "True"
        isignored = getUserIgnoreStatus(db, user) == "True"
        isplayer = not(isbot or isignored)
        if isplayer:
            players.append(user)
    return players


def aliasNick(db, user, nick):
    db.merge_nick_groups(user, nick)


def unaliasNick(db, nick):
    db.unalias_nick(nick)


def checkPlayerReset(db, user):
    """
    Check the last day the user has taken an action, if not today, set their gpts to 10
    """
    lastday = db.get_nick_value(user, "lastday", 0)
    currentday = datetime.now().day
    if lastday != currentday:
        db.set_nick_value(user, "lastday", currentday)
        setgpts(db, user, 10)
