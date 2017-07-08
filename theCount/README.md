# countBot
This is a simple IRC bot that uses the twisted IRCClient. It is essentially a random number generator.
When a game is initialized the users begin counting with one, and continue until the correct number is guesssed.

ADMIN COMMANDS

         botNick, set <userNick> <timesWon> (set timesWon for user on a reset)
         botNick, del <userNick> (delete a user from the list/winnings table)
         botNick, start (starts game)
         botNick, save (saves list of winners || also gets saved at the end of every game)
         botNick, quit (quits current game)
         botNick, users (prints list of users to console)
         botNick, restore (restores winners from save file || also restores automatically on run)
         botNick, say <msg> (sends message to channel as the bot)

  USER COMMANDS

         botNick, help (help message)
         botNick, loser (LOSER: <user who called>)
         botNick, losers (list of losers)
         botNick, winners (shows list of winners)
