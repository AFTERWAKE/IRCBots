#!/usr/bin/python

import praw
import sys
from jokesToJson import addJoke
import subprocess

def main():
    reddit = praw.Reddit(client_id='RDH7DCODcOC48g',
                         client_secret='8sSHr0222SsEg9g9Og1VOUJJz7E',
                         user_agent='getDadJokes')

    # TODO read these one by one, and I either approve or disapprove them 
    # to get sent to the dadJokes.txt file.
    with open("dadJokes.txt", "a", encoding="utf-8") as file:
		# Choose from new, hot, gilded, top, etc...
        for submission in reddit.subreddit('dadjokes').new(limit=int(sys.argv[1])):
            line_one = submission.title
            line_two = submission.selftext.strip().split("\n")[0]
            print("\n\n" + line_one)
            print(line_two)
            save = input("Save this? [y/n] (default: n) ")
            if "y" in save:
                addJoke(line_one + "\n" + line_two)


if __name__ == "__main__":
    main()