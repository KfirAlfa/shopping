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

    def bind_messages(self):
        # uf, this is not good. how can I see just the changes of the DOM? :thinking
        while True:
            time.sleep(1)
            unread_messages = self.db.get_unread_messages()
            for msg_id, msg  in unread_messages.items():
                print (msg.lines)

def main():
    connector = whastappBringConnector()
    connector.bind_messages()

if __name__ == '__main__':
    main()
