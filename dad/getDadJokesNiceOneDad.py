#!/usr/bin/python

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import csv
import sys

JOKE_XPATH = "(/html/body/div[@id='Stage']/div[@id='Container']/div[@id='Jokes']/div[@class='JokesView']/div[@class='JokesJoke']/div[@class='wrapper']/div)"

def getJoke():
  browser = webdriver.Chrome()
  browser.get("http://niceonedad.com")

  time.sleep(5)
  try:
    line_one = browser.find_element_by_xpath(JOKE_XPATH + "[1]").text
    line_two = browser.find_element_by_xpath(JOKE_XPATH + "[2]").text
    browser.close()
  except Exception as e:
    print("ERROR: Couldn't find element")
    browser.close()
    raise Exception("ERROR: Couldn't find element")
  try:
    print(line_one + ", " + line_two + "\n")
  except Exception as e:
    print("WARNING: Couldn't print this line")
  return [line_one, line_two]

def main():
  i = 0
  try:
    num_runs = int(sys.argv[1])
    print("Getting " + str(num_runs) + " dad jokes...")
  except Exception as e:
    print("No number of runs specified, defaulting to 5...")
    num_runs = 5

  while(i < num_runs):
    try:
      with open('jokes.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter='~')
        writer.writerow(getJoke())
      i += 1
    except Exception as e:
      print("Error while getting this joke... skipping...")

if __name__ == "__main__":
  main()