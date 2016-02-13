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

def etsi_title(a,first,last):
	try:
		start=a.index( first ) + len( first )
		end=a.index( last, start)
		return a[start:end]
	except ValueError:
		return ""


def avaaurl(osoite):
	alku = "<title>"
	loppu = "</title>"

	f=urllib.urlopen(osoite)
	rivit=f.readlines()
	num_lines=len(rivit)
	
	for index in range(num_lines):
		if alku in rivit[index]:
			otsikko = etsi_title(rivit[index],alku,loppu)
			return otsikko
			break


try:
	s.connect((host, port))
	print "moro kukkuu"
except Exception,e:
	print "Connection failed"
	print "meep %s" % Exception
	print "meep2 %s" % e

s.send("NICK %s\r\n" % name)
s.send("USER %s %s bla :%s\r\n" % (ident, host, realname))
s.send("JOIN :%s\r\n" % chan)

msg="www.youtube.com"

try:
	while 1:

		ircmsg = s.recv (bufsize)
		ircmsg = ircmsg.strip('\n\r')
		
		print ircmsg

		if ircmsg.find ("PING :") != -1:
			s.send("PONG :pingis\n")

		if msg in ircmsg:
			urls = findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", ircmsg)
			if urls:
				print urls[0]
				viesti=avaaurl(urls[0])
				s.send("PRIVMSG %s :%s\r\n" % (chan, viesti))
	
except KeyboardInterrupt:
	s.send("PRIVMSG %s :%s\r\n" % (chan, "Heippa"))
	print "sammutetaan bot"

s.close()
