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
host="irc2.inet.fi"
port=6667
name="belsebot"
ident="belsebot"
realname="belsebot"
chan="#ixchan"
#s=socket.socket()
#s.settimeout(400)

def term_received(sig,frame):
	s.send("PRIVMSG %s :%s\r\n" % (chan,"Jarjestelma Sammutetaan"))
	s.close()
	sys.exit(0)
	return

def checksize(uri):
#	print "checksize"
	headers={ 'User-Agent' : 'Mozilla/5.0' }
	try:
		req=urllib2.Request(uri,None,headers)
		check=0

		try:
			file=urllib2.urlopen(req,timeout=4)
			size=file.headers.get("content-length")
			file.close()
			if size==None:
				size=0
		except urllib2.HTTPError,e:
			print e
			size=0
		except urllib2.URLError,e:
			print e
			size=-1
		return int(size)

	except httplib.HTTPException:
		size=-1
		return int(size)

def etsi_title(a,first,last):
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

	headers={ 'User-Agent' : 'Mozilla/5.0' }
	req=urllib2.Request(osoite,None,headers)
		
	try:
		f=urllib2.urlopen(req)
		rivit=f.readlines()
		num_lines=len(rivit)

		for index in range(num_lines):
			if alku in rivit[index]:
				otsikko = etsi_title(rivit[index],alku,loppu)
				return otsikko
				break
	except urllib2.HTTPError,e:
		error="vamma esto"
		return error

def ircconnect(host,port,name,ident,realname,chan):
	global s
	s=socket.socket()
	s.settimeout(400)

	try:
		s.connect((host, port))
		print "Ircconnect"
		s.send("NICK %s\r\n" % name)
		s.send("USER %s %s bla :%s\r\n" % (ident, host, realname))
		s.send("JOIN :%s\r\n" % chan)
		ircloop()
	except (socket.error,socket.timeout) as err2:
		print "Connection failed"
#		print "meep %s" % Exception
		print err2
		s.close()
		time.sleep(200)
		ircconnect(host,port,name,ident,realname,chan)


def ircloop():
#	print "Ircloop"
	check=0
	msg = [None]*3
	msg[0]=".gif"
	msg[1]=".pdf"
	msg[2]=".jpg"
	lista = [None]*10
	lista[0] = "kukkuu"
	lista[1] = "moro"
	lista[2] = "vitutus on tyomiehen paras (tyo)kaveri."
	lista[3] = "et voi tietaa"
	lista[4] = "senkun nakisi"
	lista[5] = "elama on kuin pohjaton kaivo kun katson ylos naen valon joka loittonee ja kun katson alas naen pimeyden jota kohti putoan"
	lista[6] = "olen porroinen ja pehmea"
	lista[7] = "yyy mulla on taalla makuupussissa teidan jalkiruuat, houdoin niita munissani. jos joku haluaa jalkkaria niin saa tulla hakeen wryy"
	lista[8] = "ja siitakun paastin niin tulee toinen tilalle. niita on varmaan jonoks asti. yhdesta paasee eroon niin johan on toinen ottamassa sen paikan."
	lista[9] = "luulet vaan"

	vituttaa="Jos vituttaa niin mita siita suotta virtta vaantaamaan kun metsa on taynna paksu oksaisia mantyja"
	utstats="Mita niita suotta katsomaan kun tiedetaan etta Belse on paras"

	while 1:
		try:

			ircmsg = s.recv (bufsize)

			if len(ircmsg) == 0:
				break

			ircmsg = ircmsg.strip('\n\r')

#			print ircmsg

			if ircmsg.find ("PING :") != -1:
				s.send("PONG :pingis\n")

			urls = findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", ircmsg)

			if urls:
#				print urls[0]

				if msg[0] in urls[0]:
					s.send("PRIVMSG %s :%s\r\n" % (chan,"onkos toi nyt sitten joku gif"))
				elif msg[1] in urls[0]:
					s.send("PRIVMSG %s :%s\r\n" % (chan,"ei tassa nyt romaaneja ruveta lukemaan"))
				elif msg[2] in urls[0]:
					s.send("PRIVMSG %s :%s\r\n" % (chan,"toi on kylla jpg"))
				else:

					koko=checksize(urls[0])
					if koko != -1:
						maxsize=1000000
						print koko
						print urls[0]
						if koko>maxsize:
							s.send("PRIVMSG %s :%s\r\n" % (chan, "Liian iso"))
						else:
							viesti=avaaurl(urls[0])
							if viesti:
								s.send("PRIVMSG %s :%s\r\n" % (chan, viesti))
							else:
								s.send("PRIVMSG %s :%s\r\n" % (chan, "No title found"))
					else:
						s.send("PRIVMSG %s :%s\r\n" % (chan, "Timeout tai joku vammainen badstatus tai muu vastaava"))

			if ircmsg.find("!viisaus") != -1:
				num=randint(0,9)
				s.send("PRIVMSG %s :%s\r\n" % (chan, lista[num]))

			if ircmsg.find("!vituttaa") != -1:
				s.send("PRIVMSG %s :%s\r\n" % (chan, vituttaa))

			if ircmsg.find("!utstat") != -1:
				s.send("PRIVMSG %s :%s\r\n" % (chan, utstats))

			if ircmsg.find(":Belse!") != -1:
				sulje = ircmsg.split(':',2)
				if sulje[2]=="!quit":
					s.send("PRIVMSG %s :%s\r\n" % (chan, "Heippa"))
					print "sammutetaan bot"
					s.close()
					break


		except (socket.timeout,socket.error) as err:
			print "Virhe 2"
			print err
			time.sleep(200)
			ircconnect(host,port,name,ident,realname,chan)

	print "Ohjelma loppui"
	s.close()

if __name__ == "__main__":

	print "Ircbot launch"
	signal.signal(signal.SIGTERM, term_received)

	ircconnect(host,port,name,ident,realname,chan)
	

	print "Ohjelma loppui2"
	s.close()
