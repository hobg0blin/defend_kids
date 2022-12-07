from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import random
import time
import undetected_chromedriver as uc
import names
import markovify
import os
from dotenv import load_dotenv
load_dotenv()


cities = ["Dallas", "Austin", "Houston", "Hazel", "Fort Worth"]
corpus = open("./corpus.txt").read()
model = markovify.Text(corpus)
input_text = ""
for (i) in range(random.randint(1, 10)):
    input_text += model.make_sentence()

class Selenium():
    def __init__(self):
        self.driver = uc.Chrome(use_subprocess=True, version_main=os.getenv('CHROME_VERSION'))
        self.wait = WebDriverWait(self.driver, 3000000000);

    def run(self):
        print('reloading')
        self.driver.get('https://defendkidstx.com/')
        time.sleep(random.randint(5, 10))
#        self.wait.until(lambda x: self.check_captcha())
        self.wait.until(lambda x: self.check_has_button())
        time.sleep(5)
        self.fill_form()
        self.driver.close()
        self.__init__()
        self.run()

    def check_has_button(self):
        print('checking button')
        try:
            self.driver.find_element(By.XPATH, "//a[@href='#popup']").click()
            print('button found')
            return True
        except NoSuchElementException:
            print('temporarily blocked')
#            self.wait.until(lambda x: self.check_captcha())
            time.sleep(random.randint(5, 20))
            self.driver.refresh()
            return False
    def check_captcha(self):
        try:
            self.driver.find_element(By.XPATH, "//div[@class='ctp-checkbox-container']")
            print('FILL OUT CAPTCHA')
            return False
        except NoSuchElementException:
            time.sleep(random.randint(3, 10))
            print('captcha not found')
            return True
    def check_recaptcha(self):
        try:
            self.driver.find_element(By.XPATH, ("//div[@id='input_2_6']//iframe[contains(@title,'reCAPTCHA')]"))
            print('FILL OUT RECAPTCHA!')
        except NoSuchElementException:
            time.sleep(random.randint(1, 5))
            print('recaptcha not found')
            return True
        return False
    def check_exists_by_id(self, id):
        try:
            self.driver.find_element(By.ID, id)
        except NoSuchElementException:
            return False
        return True

    def fill_form(self):
        print("filling out form")
        name = names.get_full_name()
        # they have two alternate input forms, presumably to prevent me from doing things like this - this should account for both
        if (self.check_exists_by_id("input_2_1")):
            name_box = self.driver.find_element(By.ID, "input_2_1")
            name_box.send_keys(name)
            email_box = self.driver.find_element(By.ID, "input_2_3")
            email_box.send_keys(name.replace(" ", "") + str(random.randint(100000,500000)) + "@gmail.com")
            location_box = self.driver.find_element(By.ID, "input_2_4")
            location_box.send_keys(random.choice(cities) + ", TX")
            info_box = self.driver.find_element(By.ID, "input_2_5")
            info_box.send_keys(input_text)
            time.sleep(5)
            self.wait.until(lambda x: self.check_recaptcha())
#            self.wait.until(lambda x: self.check_captcha())
            try:
                self.driver.find_element(By.ID, "gform_submit_button_2").click()
            except NoSuchElementException:
                print("manually submitted")
            time.sleep(2)
            print("form submitted - running again")

        elif (self.check_exists_by_id("et_pb_contact_name_0")):
            name_box = self.driver.find_element(By.ID, "et_pb_contact_name_0")
            name_box.send_keys(name)
            email_box = self.driver.find_element(By.ID, "et_pb_contact_email_0")
            email_box.send_keys(name.replace(" ", "") + str(random.randint(100000,500000)) + "@gmail.com")
            location_box = self.driver.find_element(By.ID, "et_pb_contact_location_of_show_0")
            location_box.send_keys(random.choice(cities) + ", TX")
            info_box = self.driver.find_element(By.ID, "et_pb_contact_other_info_0")
            info_box.send_keys(input_text)
#            self.wait.until(lambda x: self.check_captcha())
#            self.wait.until(lambda x: self.check_recaptcha())
            try:
                self.driver.find_element(By.XPATH, "//button[@class='et_builder_submit_button']").click()
            except NoSuchElementException:
                print("manually submitted")

            print("form submitted")
        else:
            print("Looks like they may have found a way to beat this scraper. Perhaps you could help update it!")


form_filler = Selenium()
form_filler.run()
