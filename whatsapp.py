#!/usr/bin/python3
import time
from PIL import Image

import io
from strcuts import Message

from selenium import webdriver 
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException
from selenium.webdriver.support import expected_conditions as EC


def find_div_that_contain_testid(element: WebElement, testid):
    return element.find_elements(
        By.XPATH,
        "//div[contains(@data-testid, '%s')]" % testid
    )

def find_all_div_by_testid(element: WebElement, testid):
    try:
        return WebDriverWait(element, 10).until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//div[@data-testid='%s']" % testid))
        )
    except TimeoutException:
        # try again, but don't wait forever.
        print("timeout, try again to find %s " % testid)
        return WebDriverWait(element, 100).until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//div[@data-testid='%s']" % testid))
        )

def is_testid_exist(element, testid) -> bool:
    try:
        WebDriverWait(element, 0).until(
        EC.presence_of_all_elements_located((
            By.XPATH,
            "//div[@data-testid='%s']" % testid))
        )
    except TimeoutError:
        #testid does not exist
        return False
    return True

def find_div_by_testid(element: WebElement, testid):
    try:
        return WebDriverWait(element, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@data-testid='%s']" % testid))
        )
    except TimeoutException:
        # try again, but don't wait forever.
        print("timeout, try again to find %s " % testid)
        return WebDriverWait(element, 100).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@data-testid='%s']" % testid))
        )

class Whatsapp(object):
    # whatsapp block headless user agents, so we need a fake one
    VALID_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    LOGIN_PAGE = "https://web.whatsapp.com/"
    # TODO: make configurable / auto find chrome
    CHROME_PATH = "/Users/kfiralfandary/.wdm/drivers/chromedriver/mac64/109.0.5414/chromedriver"
    SHOPPING_CONVERSATION = 'shopping_list'

    def __init__(self, conversation_name=SHOPPING_CONVERSATION) -> None:
        self._browswer = self._init_selenuim_driver()
        self._conversation_name = conversation_name
        self._last_msg_id = None

    @classmethod
    def _init_selenuim_driver(cls) -> webdriver.Chrome:
        options =  webdriver.ChromeOptions()
        #options.headless = True
        #options.add_argument("user-agent='%s'" % cls.VALID_USER_AGENT)
        #TODO -> fix this...
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")

        chrom_services = Service(cls.CHROME_PATH)
        return webdriver.Chrome(service=chrom_services, options=options)
        
    def login(self):
        self._browswer.get(self.LOGIN_PAGE)
        qr_html_elements = find_div_by_testid(self._browswer, 'qrcode')

        qr_pic = io.BytesIO(qr_html_elements.screenshot_as_png)
        qr = Image.open(qr_pic)
        qr.show()

        # don't finish log-in as long as the qr code is stil exist 
        qr_is_not_exist = False
        while not qr_is_not_exist:
            try:
                qr_is_not_exist = WebDriverWait(self._browswer, 5).until_not(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-testid='qrcode']"))
                )
            except TimeoutException:
                pass
        pass
            

    def _open_shopping_conversation(self):

        shopping_list_id=None
        search_box = find_div_by_testid(self._browswer, 'chat-list-search')
        search_box.click()
        search_box.send_keys("shopping")
        chat_list = find_div_by_testid(self._browswer, 'chat-list')
        conversations = find_all_div_by_testid(chat_list, 'cell-frame-container')
        for conv_id, conversation in enumerate(conversations):
            displayed_text = conversation.text.split("\n")[0]
            if displayed_text == self._conversation_name:
                shopping_list_id = conv_id

        #need to search for it
        if shopping_list_id is None:
            qr_pic = io.BytesIO(self._browswer.screenshot_as_png)
            qr = Image.open(qr_pic)
            qr.show()
            self._browswer.close()
            raise Exception("can't find shopping_list_id")
        shopping_conv = conversations[shopping_list_id]
        shopping_conv.click()

    def _read_messages(self) -> list[Message]:
        conversation_panel = find_div_by_testid(self._browswer, 'conversation-panel-messages')
        messages_web_elements = find_div_that_contain_testid(conversation_panel, 'conv-msg')
        messages = []
        for msg in messages_web_elements:
            # if we see profile picture, it means that the first line of the message is the name
            # empty list means no profile pic
            is_msg_with_profile_pic = not(is_testid_exist(msg, "group-chat-profile-picture"))
            print("DBG", msg.text, is_msg_with_profile_pic)
            messages.append(Message(msg, is_msg_with_profile_pic))
        return messages
    
    def get_messages(self) -> list[Message]:
        self._open_shopping_conversation()
        messages = self._read_messages()
        self._last_msg_id = messages[-1].id
        return messages
    
    def bind_for_new_messages(self):
        while True:
            time.sleep(1)
            messages = self._read_messages()
            if messages[-1].id == self._last_msg_id:
                continue
            # we got new messages!
            last_msg_index = [msg.id for msg in messages].index(self._last_msg_id)
            messages = messages[last_msg_index:]
            yield messages
