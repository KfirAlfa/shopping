#!/usr/bin/python3

import whatsapp
import time
import strcuts

db = strcuts.PickleMsgDB()

def main():
    start_wahtsapp()

def start_wahtsapp():
    WA = whatsapp.Whatsapp()
    WA.print_qr()
    while True:
        time.sleep(1)
        messaegs = WA.get_messages()
        for msg in messaegs:
            db.write(msg)
        pass
        unread_messages = db.get_unread_messages()
        for msg_id, msg  in unread_messages.items():
            print (msg.lines)

if __name__ == '__main__':
    main()