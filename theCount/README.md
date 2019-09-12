# countBot
This is a simple IRC bot that uses the twisted IRCClient. It is essentially a random number generator.
When a game is initialized the users begin counting with one, and continue until the correct number is guesssed.

ADMIN COMMANDS

         botNick, set <userNick> <timesWon> (set timesWon for user on a reset)
         botNick, del <userNick> (delete a user from the list/winnings table)
         botNick, start (starts game)
         botNick, save (saves list of winners || also gets saved at the end of every game)
         botNick, stop (quits current game)
         botNick, users (prints list of users to console)
         botNick, restore (restores winners from save file || also restores automatically on run)
         botNick, say <msg> (sends message to channel as the bot)
         botNick, me <me> (sends a /me message to the channel as the bot)
         botNick, mute <user> (mutes a user by IP, they will be ignored for commands and will not be able to play the game)
         botNick, unmute <user> (undoes the actions of the `mute` command)
         botNick, whois <user> (Gives the IP address of a user on the server)
         botNick, mock <user> (Mocks the user and shows their current points)
         botNick, pmock <user> (Everything the user says is mocked)
         botNick, unpmock <user> (Undoes the pmock command)
         botNick, quit <msg>{optional} (the bot leaves the channel, with an optional quit message)

  USER COMMANDS

         botNick, help (help message)
         botNick, loser (LOSER: <user who called>)
         botNick, losers (list of losers)
         botNick, winners (shows list of winners)
         botNick, wieners (shows your wiener count for the day)
         botNick, rules (shows list of rules)
         botNick, version (shows version + link to github)
         botNick, words (shows winning words)

## Install and run

Create a virtual environment and get Twisted:

    virtualenv -p /usr/bin/python3 venv
    . venv/bin/activate
    pip install Twisted

Run the bot:

    python3 countBot.py
