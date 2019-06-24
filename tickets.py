from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

#opening of page
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get('https://cws.auburn.edu/aufstc')
print("Page opened")
#username and password input
text_area = driver.find_element_by_xpath("//input[@name='username']")
text_area.send_keys("brm0029")
text_area = driver.find_element_by_xpath("//input[@name='password']")
text_area.send_keys("Robotic12")
submit_button = driver.find_element_by_xpath("//input[@name='submit']")
submit_button.click()
print("Login Successful")
#go to free ticket page
submit_button = driver.find_element_by_xpath("//a[@class='lazy item freeTicket']")
submit_button.click()
driver.quit()
print("You did it")
