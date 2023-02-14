#!/usr/bin/python3
import time
from PIL import Image

import io
from strcuts import Message

from selenium import webdriver 
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 


def find_div_that_contain_testid(element: WebElement, testid):
    return element.find_elements(
        By.XPATH,
        "//div[contains(@data-testid, '%s')]" % testid
    )

def find_div_by_testid(element: WebElement, testid):
    return element.find_elements(
        By.XPATH,
        "//div[@data-testid='%s']" % testid
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

    @classmethod
    def _init_selenuim_driver(cls) -> webdriver.Chrome:
        options =  webdriver.ChromeOptions()
        options.headless = True
        #options.add_argument("user-agent='%s'" % cls.VALID_USER_AGENT)
        #TODO -> fix this...
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")

        chrom_services = Service(cls.CHROME_PATH)
        return webdriver.Chrome(service=chrom_services, options=options)
        
    def print_qr(self):
        self._browswer.get(self.LOGIN_PAGE)
        qr_html_elements = find_div_by_testid(self._browswer, 'qrcode')
        was_qr_printed = False
        time.sleep(5)
        # If no qr and qr was not printed, show it
        while len(qr_html_elements) == 0 or not was_qr_printed:
            # A stuipd way to wait for whatssapp to login
            qr_html_elements = find_div_by_testid(self._browswer, 'qrcode')
            if len(qr_html_elements) == 0:
                continue
            qr_pic = io.BytesIO(qr_html_elements[0].screenshot_as_png)
            qr = Image.open(qr_pic)
            qr.show()
            was_qr_printed = True
            #TODO -> change with ""
            time.sleep(10)
            

    def _open_shopping_conversation(self):
        chat_list = find_div_by_testid(self._browswer, 'chat-list')[0]
        conversations = find_div_by_testid(chat_list, 'cell-frame-container')

        shopping_list_id=None
        for conv_id, conversation in enumerate(conversations):
            displayed_text = conversation.text.split("\n")[0]
            if displayed_text == self._conversation_name:
                shopping_list_id = conv_id

        #need to search for it
        shopping_conv = conversations[shopping_list_id]
        shopping_conv.click()

    def _read_messages(self) -> list[Message]:
        conversation_panel = find_div_by_testid(self._browswer, 'conversation-panel-messages')[0]
        messages_web_elements = find_div_that_contain_testid(conversation_panel, 'conv-msg')
        messages = []
        for msg in messages_web_elements:
            # if we see profile picture, it means that the first line of the message is the name
            # empty list means no profile pic
            is_msg_with_profile_pic = not(bool(find_div_by_testid(msg, "group-chat-profile-picture")))
            messages.append(Message(msg, is_msg_with_profile_pic))
        return messages
    
    def get_messages(self) -> list[Message]:
        self._open_shopping_conversation()
        return self._read_messages()