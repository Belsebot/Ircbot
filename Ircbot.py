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
s.settimeout(400)

def etsi_title(a,first,last):				#Greps line which is between <title> and </title>
	try:
		start=a.index( first ) + len( first )
		end=a.index( last, start)
		return a[start:end]
	except ValueError:
		return ""


def avaaurl(osoite):					#Loads given url and greps Title
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


def ircconnect(host,port,name,ident,realname,chan):			#Irc connect
	try:
		s.connect((host, port))
		print "moro kukkuu"
		s.send("NICK %s\r\n" % name)
		s.send("USER %s %s bla :%s\r\n" % (ident, host, realname))
		s.send("JOIN :%s\r\n" % chan)
	except Exception,socket.error:
		print "Connection failed"
		print "meep %s" % Exception
		time.sleep(5)
		ircconnect(host,port,name,ident,realname,chan)


ircconnect(host,port,name,ident,realname,chan)

msg="www.youtube.com"						#Message you want to lookup

while 1:
	try:

		ircmsg = s.recv (bufsize)

		if len(ircmsg) == 0:
			break

		ircmsg = ircmsg.strip('\n\r')

		print ircmsg

		if ircmsg.find ("PING :") != -1:		#keep alive
			s.send("PONG :pingis\n")

		if msg in ircmsg:				#if given string founds
			urls = findall("http[s]?://www.youtube.com/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),])+",ircmsg)
			url=len(urls)
			if urls:				#if given url is correct
				viesti=avaaurl(urls[0])		#gets title for given url
				if viesti:			#if title is found
					s.send("PRIVMSG %s :%s\r\n" % (chan, viesti))		#send title to channel
				else:
					s.send("PRIVMSG %s :%s\r\n" % (chan, "No title found"))	#else send not found

		if ircmsg.find(":Belse!") != -1:		#if user Belse 
			sulje = ircmsg.split(':',2)
			if sulje[2]=="!quit":			#send message !quit
				s.send("PRIVMSG %s :%s\r\n" % (chan, "Heippa"))	
				print "sammutetaan bot"		#close bot
				s.close()
				break


	except socket.timeout:
		ircconnect(host,port,name,ident,realname,chan)
		break



s.close()

