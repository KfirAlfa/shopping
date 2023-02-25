#!/usr/bin/python3

import whatsapp
import time
import strcuts
import bring


class whastappBringConnector():
    def __init__(self) -> None:
        try:
            #self.listAPI = bring.myBring()
            self.WA = whatsapp.Whatsapp()
            self.db = strcuts.PickleMsgDB()

            #self.listAPI.login()
            self.WA.login()
            self._init_db()
        except Exception as err:
            print("unexpected error: %s", err)
            raise err

    def _init_db(self):
        '''
        Make sure that all the new messages are in the DB
        '''
        messaegs = self.WA.get_messages()
        for msg in messaegs:
            self.db.write_if_not_exist(msg)
        
    def send_to_bring(self, msg):
        print (msg.lines)

    def handle_old_messags(self):
        unread_messages = self.db.get_unread_messages()
        for msg_id, msg  in unread_messages.items():
            self.send_to_bring(msg)

    def bind_messages(self):
        for unread_messages in self.WA.bind_for_new_messages:
            for msg_id, msg  in unread_messages.items():
                self.db.write_if_not_exist(msg)
                self.send_to_bring(msg)

def main():
    connector = whastappBringConnector()
    connector.handle_old_messags()
    connector.bind_messages()

if __name__ == '__main__':
    main()
