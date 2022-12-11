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
import sys
from anticaptchaofficial.recaptchav2proxyless import *
from dotenv import load_dotenv
load_dotenv()


cities = ["Dallas", "Austin", "Houston", "Hazel", "Fort Worth"]
corpus = open("./corpus.txt",encoding='utf8').read()
model = markovify.Text(corpus)
input_text = ""
for (i) in range(random.randint(1, 10)):
    input_text += model.make_sentence()

# [name, email, location, info]
form_types = [
    ["input_2_1", "input_2_3", "input_2_4", "input_2_5", "gform_submit_button_2"],
    ["et_pb_contact_name_0", "et_pb_contact_email_0", "et_pb_contact_location_of_show_0", "et_pb_contact_other_info_0", "et_builder_submit_button"],
]


submit_buttons = [
    # [By.ID, "gform_submit_button_2"],
    [By.XPATH, "//button[@type='submit']"]
]

class FormType():
    def __init__(self, name, email, location, info):
        self.name = name
        self.email = email
        self.location = location
        self.info = info


class Selenium():
    use_solver = False
    def __init__(self):
        self.driver = uc.Chrome(use_subprocess=True, version_main=os.getenv('CHROME_VERSION'))
        self.wait = WebDriverWait(self.driver, 3000000000)
        self.solver = recaptchaV2Proxyless()

    def run(self):
        print('reloading')
        self.driver.get('https://defendkidstx.com/')
        time.sleep(random.randint(5, 10))
        # setup anti-captcha solver
        self.init_solver()
        if not self.use_solver:
            print("Please complete captcha")
            self.wait.until(lambda x: self.check_captcha())

        self.wait.until(lambda x: self.check_has_button())
        time.sleep(1)
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
            if not self.use_solver:
                self.wait.until(lambda x: self.check_captcha())
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
            element = self.driver.find_element(By.ID, id)
            if element:
                return element.is_displayed()
        except NoSuchElementException:
            return False
    def get_form_type(self) -> FormType:
        for check_type in form_types:
            print(f"checking name {check_type[0]}")
            print(check_type)
            form_type = FormType(check_type[0], check_type[1], check_type[2], check_type[3])
            try:
                self.driver.find_element(By.ID, form_type.name).is_displayed()
                return form_type
                # if self.check_exists_by_id(form_type.name):
                    # return form_type
            except NoSuchElementException:
                print(f"not {form_type.name}")
                continue

        print("Looks like they may have found a way to beat this scraper. Perhaps you could help update it!")
        self.run()
    def submit(self):
        for button in submit_buttons:
            print(f"trying button {button[1]}")
            try:
                self.driver.find_element(button[0], button[1]).click()
                return
        except NoSuchElementException:
                print(f"couldn't find button {button[1]}")
    def init_solver(self):
        api_key = os.getenv("ANTICAPTCHA_API_KEY")
        if len(api_key) == 0:
            print("No Anti-Captcha API Key Provided, disabling")
            return
        if len(api_key) != 32:
            print(f"Invalid Anti-Captcha API Key: {api_key}")
            return
        self.solver.set_verbose(1)
        self.solver.set_key(api_key)
        self.solver.set_website_url("https://www.defendkidstx.com/")
        self.solver.set_website_key("6Lf4g08jAAAAADLHLYYA6jsr0qXWgOM_btlJP3iD")
        # use_solver determines if anything runs when any anti-captcha functions is called
        self.use_solver = True

    def get_captcha_solution(self) -> str:
        if not self.use_solver:
            print("Anti-Captcha Disabled")
            return ""
        print("[BEGIN CAPTCHA SOLVE]")
        g_response = self.solver.solve_and_return_solution()
        if g_response != 0:
            print("g-response: "+g_response)
        else:
            print("task finished with error "+self.solver.error_code)
            sys.exit(2)
        print("[END CAPTCHA SOLVE]")
        return g_response

    def fill_captcha(self, captcha_solution):
        if not self.use_solver:
            return True
        try:
            element = self.driver.find_element(
                By.XPATH, ("//textarea[@name='g-recaptcha-response']"))
            element.__setattr__("value", captcha_solution)
            # element.send_keys(captcha_solution)
        except NoSuchElementException:
            print("could not find recaptcha textarea")
            return False
        return True

    def fill_form(self):
        print("filling out form")
        name = names.get_full_name()
        # they have two alternate input forms, presumably to prevent me from doing things like this - this should account for both
        form_type = self.get_form_type()
        captcha_solution = self.get_captcha_solution()
        try:
            name_box = self.driver.find_element(By.ID, form_type.name)
            name_box.send_keys(name)
        except:
            print("error filling form, reloading page")
            self.driver.get("https://defendkidstx.com/")
            return
        email_box = self.driver.find_element(By.ID, form_type.email)
        email_box.send_keys(name.replace(
                " ", "") + str(random.randint(100000, 500000)) + "@gmail.com")
        location_box = self.driver.find_element(By.ID, form_type.location)
        location_box.send_keys(random.choice(cities))
        info_box = self.driver.find_element(By.ID, form_type.info)
            info_box.send_keys(input_text)
        time.sleep(1)

        if not self.fill_captcha(captcha_solution):
            print("error filling captcha")
            
        time.sleep(1)
        self.submit()

            time.sleep(2)
            print("form submitted - running again")


form_filler = Selenium()
form_filler.run()
