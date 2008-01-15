import os
import sys
if os.sys.platform == 'win32':
	sys.path.append("..\\..\\src") # - dla windowsa
else:
	sys.path.append("../") # - dla linuksa
from Contacts import *
from pygglib import GGSession
from Helpers import *
from GGConstans import *
import time

#
# 11327271, haslo eto2007 
#

def login_ok_event_handler(sender, args):
	print 'Zalogowano.'

def msg_recv_event_handler(sender, args):
	print 'Message received:'
        print 'sender:', args.sender
	print 'seq:', args.seq
	print 'msg_class:', GGMsgTypes.reverse_lookup(args.msg_class)
	print 'message:', args.message
	print
	
def on_unknown_packet_event_handler(sender, args):
	print 'Unknow packet received: type: %d, length: %d' % (args.type, args.length)
	print
	
def on_send_msg_ack_event_handler(sender, args):
	print 'msg_send_ack received: status: %s, recipient: %d, seq: %d' % (GGMsgStatus.reverse_lookup(args.status), args.recipient, args.seq)
	
def on_pubdir_recv_event_handler(sender, args):
	print 'PubDir type', args.req_type
	print 'PubDir sequence numer', args.seq
	entries = args.reply.split("\0\0")
	for item in entries:
		print request_to_dict(item)
	print
	
def on_userlist_reply(sender, args):
	print 'UserListReply'
	assert type(args.contacts_list) == ContactsList
	print

if __name__ == "__main__":
	session = GGSession(uin = 11327271, password = 'eto2007')
	session.register('on_login_ok', login_ok_event_handler)
	session.register('on_msg_recv', msg_recv_event_handler)
	session.register('on_unknown_packet', on_unknown_packet_event_handler)
	session.register('on_send_msg_ack', on_send_msg_ack_event_handler)
	session.register('on_pubdir_recv', on_pubdir_recv_event_handler)
        session.register('on_userlist_reply', on_userlist_reply)
	session.login()
        session.import_contacts_list()
        session.export_contacts_list("kontakty.txt")
	session.logout()
	x = raw_input()
