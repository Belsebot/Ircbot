import sys
import socket
import string 
import imp
import os
import thread
import urllib
from re import findall


bufsize=2048
host=""
port=6667
name="belsebot"
ident="belsebot"
realname="belsebot"
chan="#"
s=socket.socket()

def etsi_title(a,first,last):			#greps Title from webpage
	try:
		start=a.index(first) + len(first)
		end=a.index(last, start)
		return a[start:end]		#returns whats between searched words
	except ValueError:
		return ""


def avaaurl(osoite):				#opens given webpage
	alku = "<title>"
	loppu = "</title>"

	f=urllib.urlopen(osoite)
	rivit=f.readlines()
	num_lines=len(rivit)
	
	for index in range(num_lines):	
		if alku in rivit[index]:					#search <title>
			otsikko = etsi_title(rivit[index],alku,loppu)		#gets whats between <title> and </title>
			return otsikko						#returns Title
			break


try:
	s.connect((host, port))				#connect irc server
	print "moro kukkuu"
except Exception,e:
	print "Connection failed"
	print "meep %s" % Exception
	print "meep2 %s" % e

s.send("NICK %s\r\n" % name)
s.send("USER %s %s bla :%s\r\n" % (ident, host, realname))
s.send("JOIN :%s\r\n" % chan)				#joins channel

msg="www.youtube.com"					#webpage where you want grep titles

try:							#main loop
	while 1:

		ircmsg = s.recv (bufsize)		#gets messages
		ircmsg = ircmsg.strip('\n\r')
		
		print ircmsg

		if ircmsg.find ("PING :") != -1:	#keep alive
			s.send("PONG :pingis\n")

		if msg in ircmsg:			#if message holds wanted webpage
			urls = findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", ircmsg)
			if urls:							#if given message is url
				print urls[0]
				viesti=avaaurl(urls[0])					
				s.send("PRIVMSG %s :%s\r\n" % (chan, viesti))		#send title to channel
	
except KeyboardInterrupt:
	s.send("PRIVMSG %s :%s\r\n" % (chan, "Heippa"))
	print "sammutetaan bot"

s.close()
