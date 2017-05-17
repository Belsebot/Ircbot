import sys
import socket
import string 
import signal
import imp
import os
import thread
import urllib2
import time
import httplib
from re import findall
from random import randint


bufsize=2048
host=""
port=6667
name="belsebot"
ident="belsebot"
realname="belsebot"
chan="#chan"
#s=socket.socket()
#s.settimeout(400)

def term_received(sig,frame):
	s.send("PRIVMSG %s :%s\r\n" % (chan,"Jarjestelma Sammutetaan"))		#sends system shutdown message to channel
	s.close()
	sys.exit(0)								#Shutdowns bot
	return

def checksize(uri):
#	print "checksize"
	headers={ 'User-Agent' : 'Mozilla/5.0' }	#sets User-agent info what server sees
	try:
		req=urllib2.Request(uri,None,headers)
		check=0

		try:
			file=urllib2.urlopen(req,timeout=4)	#opens given url
			size=file.headers.get("content-length")	#gets page size if that is given
			file.close()
			if size==None:				#if dont get page size
				size=0				#set size to 0
		except urllib2.HTTPError,e:			#http Error
			print e
			size=0
		except urllib2.URLError,e:			#url Error
			print e
			size=-1
		return int(size)

	except httplib.HTTPException:	#http Error
		size=-1
		return int(size)

def etsi_title(a,first,last):		#gets title
#	print "etsititle"
	try:
		start=a.index(first) + len(first)
		end=a.index(last, start)
		return a[start:end]
	except ValueError:
		return ""


def avaaurl(osoite):
#	print "avaaurl"
	alku = "<title>"
	loppu = "</title>"

	headers={ 'User-Agent' : 'Mozilla/5.0' }	#sets user agent info that server can see
	req=urllib2.Request(osoite,None,headers)
		
	try:
		f=urllib2.urlopen(req)		#opens given url
		rivit=f.readlines()		#read page lines
		num_lines=len(rivit)		#and counts lines

		for index in range(num_lines):
			if alku in rivit[index]:	#search title
				otsikko = etsi_title(rivit[index],alku,loppu)
				return otsikko
				break
	except urllib2.HTTPError,e:		#http error
		error="vamma esto"
		return error

def ircconnect(host,port,name,ident,realname,chan):
	global s
	s=socket.socket()
	s.settimeout(400)

	try:
		s.connect((host, port))			#connects to given host and port
		print "Ircconnect"
		s.send("NICK %s\r\n" % name)		#sets name
		s.send("USER %s %s bla :%s\r\n" % (ident, host, realname))
		s.send("JOIN :%s\r\n" % chan)		#joins irc channel
		ircloop()				#starts bot
	except (socket.error,socket.timeout) as err2:		#socket error
		print "Connection failed"
#		print "meep %s" % Exception
		print err2
		s.close()
		time.sleep(200)					#wait
		ircconnect(host,port,name,ident,realname,chan)	#and reconnect


def ircloop():
#	print "Ircloop"
	check=0
	msg = [None]*3
	msg[0]=".gif"			#block some files
	msg[1]=".pdf"			#block some files
	msg[2]=".jpg"			#block some files
	lista = [None]*10		#random msg what bot can say
	lista[0] = "msg"
	lista[1] = "msg"
	lista[2] = "msg"
	lista[3] = "msg"
	lista[4] = "msg"
	lista[5] = "msg"
	lista[6] = "msg"
	lista[7] = "msg"
	lista[8] = "msg"
	lista[9] = "msg"

	vituttaa="msg"
	utstats="msg"

	while 1:			#main loop
		try:

			ircmsg = s.recv (bufsize)	#receives message

			if len(ircmsg) == 0:		#if no messages then break
				break

			ircmsg = ircmsg.strip('\n\r')	#strips end of lines

#			print ircmsg

			if ircmsg.find ("PING :") != -1:	#keep alive
				s.send("PONG :pingis\n")

			urls = findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", ircmsg)

			if urls:		#if detected url
#				print urls[0]

				if msg[0] in urls[0]:		#if url contains gif then breaks
					s.send("PRIVMSG %s :%s\r\n" % (chan,"onkos toi nyt sitten joku gif"))
				elif msg[1] in urls[0]:		#if url contains pdf then breaks
					s.send("PRIVMSG %s :%s\r\n" % (chan,"ei tassa nyt romaaneja ruveta lukemaan"))
				elif msg[2] in urls[0]:		#if url contains jpg then breaks
					s.send("PRIVMSG %s :%s\r\n" % (chan,"toi on kylla jpg"))
				else:

					koko=checksize(urls[0])		#check page size
					if koko != -1:			
						maxsize=1000000		#pages maxsize
						print koko
						print urls[0]
						if koko>maxsize:	#if pages is too big then sends msg that says its too big
							s.send("PRIVMSG %s :%s\r\n" % (chan, "Liian iso"))
						else:
							viesti=avaaurl(urls[0])		#opens given page address
							if viesti:			#if founds title for given page
								s.send("PRIVMSG %s :%s\r\n" % (chan, viesti))	#then send it to channel
							else:				#else send no title found
								s.send("PRIVMSG %s :%s\r\n" % (chan, "No title found"))
					else:				#if detected some error send error message
						s.send("PRIVMSG %s :%s\r\n" % (chan, "Timeout tai joku vammainen badstatus tai muu vastaava"))

			if ircmsg.find("!viisaus") != -1:		#if someone says !viisaus bots says random message
				num=randint(0,9)
				s.send("PRIVMSG %s :%s\r\n" % (chan, lista[num]))

			if ircmsg.find("!vituttaa") != -1:		#same as above but specified message
				s.send("PRIVMSG %s :%s\r\n" % (chan, vituttaa))

			if ircmsg.find("!utstat") != -1:		#same
				s.send("PRIVMSG %s :%s\r\n" % (chan, utstats))

			if ircmsg.find(":Belse!") != -1:	#if detected that given user..
				sulje = ircmsg.split(':',2)	#
				if sulje[2]=="!quit":		#..commands !quit then shutdowns bot
					s.send("PRIVMSG %s :%s\r\n" % (chan, "Heippa"))
					print "sammutetaan bot"
					s.close()
					break


		except (socket.timeout,socket.error) as err:	#timeout or socket error
			print "Virhe 2"
			print err
			time.sleep(200)				#wait
			ircconnect(host,port,name,ident,realname,chan)	#reconnect

	print "Ohjelma loppui"
	s.close()

if __name__ == "__main__":

	print "Ircbot launch"
	signal.signal(signal.SIGTERM, term_received)		#Activates term_recceived function if detected system shutdown

	ircconnect(host,port,name,ident,realname,chan)		#ircconnet
	

	print "Ohjelma loppui2"
	s.close()
