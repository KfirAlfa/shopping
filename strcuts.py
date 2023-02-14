#!/usr/bin/python3

import pickle
import os.path
from selenium.webdriver.remote.webelement import WebElement

class Message(object):
    def __init__(self, msg: WebElement, is_msg_with_profile_pic: bool):
        
        msg_metadata = msg.get_attribute("data-testid")
        # format metdata is ['conv-msg-true', '120363029846531720@g.us', '3EB04E4AFFB48D273D57', '972544311232@c.us']
        try:
            _, self.dst, self.id, self.src = msg_metadata.split("_")
        except Exception as e:
            print("this is msg_metadata  ", msg_metadata)
            print(e)
            
        self.lines =  msg.text.split("\n")[1:-1] if is_msg_with_profile_pic else msg.text.split("\n")[:-1] 
        self._was_read = False
    
class MsgDB(object):
    def write(self, msg: Message):
       raise NotImplementedError()
    def get_unread_messages(self, uid) -> Message:
       raise NotImplementedError()

class PickleMsgDB(MsgDB):
    DB_PATH = "messages.db"
    
    def __init__(self) -> None:
        super().__init__()
        self.messages = {}
        if not os.path.exists(self.DB_PATH):
            self._create_db()
        self._load_from_db()

    def _create_db(self):
        with open(self.DB_PATH, "wb") as dbfile:
            pickle.dump(self.messages, dbfile, pickle.HIGHEST_PROTOCOL)

    def _load_from_db(self):
        with open(self.DB_PATH, "rb") as dbfile:
            self.messages = pickle.load(dbfile)

    def _dump_messages_state_to_db(self):
        with open(self.DB_PATH, "+wb") as dbfile:
            pickle.dump(self.messages, dbfile, pickle.HIGHEST_PROTOCOL)

    def _mark_msg_as_read(self, msgID):
        self.messages[msgID]._was_read = True
        self._dump_messages_state_to_db()

    def write(self, msg: Message):
        #only write to DB if message does not exits
        if msg.id not in self.messages:
            self.messages[msg.id] = msg
            self._dump_messages_state_to_db()
    
    def get_unread_messages(self) -> list[Message]:
        messages = {}
        self._load_from_db()
        for msg in self.messages.values():
            if not msg._was_read:
                self._mark_msg_as_read(msg.id)
                messages[msg.id] = msg
        return messages

class Mock(WebElement):
    def __init__(self, parent, id_):
        super().__init__(parent, id_)
    def get_attribute(self, name):
        return range(4)
    @property
    def text(self) -> str:
        """The text of the element."""
        return ""

def generate_msg_for_test(dst, id, src, lines):
    msg = Message(Mock(None, None))
    msg.dst, msg.id, msg.src, msg.lines = dst, id, src, lines
    return msg
    
def test_pickle_db():
    messages = [
        generate_msg_for_test(
            '120363029846531720@g.us', '3EB0C16380F5D67078B8', '972544311232@c.us',
            ['this', 'is', 'with', 'lines']
        ),
        generate_msg_for_test(
             '120363029846531720@g.us', '3EB06A9D9819CB6EEC51', '972544311232@c.us',
            ['\\']
        ),
        generate_msg_for_test(
            '120363029846531720@g.us', '3A46EB737D4F48E654CB', '972544311232@c.us',
            ['.']
        ),
    ]
    db = PickleMsgDB()
    for m in messages:
        print(m.lines, m._was_read)
    for msg in messages:
        db.write(msg)
    
    print("done")
    print("first", db.get_unread_messages())
    print("second", db.get_unread_messages())
