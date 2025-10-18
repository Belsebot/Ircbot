import sys
import socket
import string
import signal
import imp
import os
import thread
import urllib2
import requests
import time
import httplib
import re
from datetime import datetime
from datetime import timedelta
from re import findall
from random import randint


bufsize=2048
host="IRC SERVER"
port=6667
name="belsebot"
ident="belsebot"
realname="belsebot"
chan="IRC CHANNEL"

def term_received(sig,frame):
	s.send("PRIVMSG %s :%s\r\n" % (chan,"Jarjestelma Sammutetaan"))
	s.close()
	sys.exit(0)
	return

def get_train(mista,mihin):
	url = "http://rata.digitraffic.fi/api/v1/live-trains/station/{}/{}?limit=3".format(mista,mihin)
	data = requests.get(url)

	return data.json()

def kello_offset():
	now=datetime.now()
	utc=datetime.utcnow()

	local_h = int(now.strftime("%H"))
	utc_h = int(utc.strftime("%H"))

	offset = local_h - utc_h

	return offset

def asemat(mista,mihin):
#	print ("asemat:",mista,mihin)
	tulostajuna=[None]*3
	offset=kello_offset()

	if (mista == mihin):
		mista = "toijala"
		mihin = "tampere"

	if (mista == "toijala"):
		mista_ = "TL"
	elif (mista == "viiala"):
		mista_ = "VIA"
	elif (mista == "tampere"):
		mista_ = "TPE"
	elif (mista == "hameenlinna"):
		mista_ = "HL"
	elif (mista == "oulu"):
		mista_ = "OL"
	elif (mista == "rovaniemi"):
		mista_ = "ROI"
	elif (mista == "jyvaskyla"):
		mista_ = "JY"
	elif (mista == "tikkurila"):
		mista_ = "TKL"
	elif (mista == "helsinki"):
		mista_ = "HKI"
	elif (mista == "turku"):
		mista_ = "TKU"
	elif (mista == "turkusatama"):
		mista_ = "TUS"
	else:
		mista_ = "TL"
		mista = "toijala"
		mihin_ = "TPE"
		mihin = "tampere"

	if (mihin == "toijala"):
		mihin_ = "TL"
	elif (mihin == "viiala"):
		mihin_ = "VIA"
	elif (mihin == "tampere"):
		mihin_ = "TPE"
	elif (mihin == "hameenlinna"):
		mihin_ = "HL"
	elif (mihin == "oulu"):
		mihin_ = "OL"
	elif (mihin == "rovaniemi"):
		mihin_ = "ROI"
	elif (mihin == "jyvaskyla"):
		mihin_ = "JY"
	elif (mihin == "tikkurila"):
		mihin_ = "TKL"
	elif (mihin == "helsinki"):
		mihin_ = "HKI"
	elif (mihin == "turku"):
		mihin_ = "TKU"
	elif (mihin == "turkusatama"):
		mihin_ = "TUS"
	else:
		mihin_ = "TPE"
		mihin = "tampere"
		mista_ = "TL"
		mista = "toijala"

	junat=get_train(mista_,mihin_)

	for a in range(0,3):

		juna=(junat[a]['trainNumber'])
		luku=len(junat[a]['timeTableRows'])

		for b in range(0,luku):

			asema=(junat[a]['timeTableRows'][b]['stationShortCode'])
			tyyppi=(junat[a]['timeTableRows'][b]['type'])
			pysahtyy=(junat[a]['timeTableRows'][b]['trainStopping'])
			raide=(junat[a]['timeTableRows'][b]['commercialTrack'])
			aika=(junat[a]['timeTableRows'][b]['scheduledTime'])

			aika_asetus=datetime.strptime(aika,'%Y-%m-%dT%H:%M:%S.%fZ')
			local_aika=aika_asetus + timedelta(hours=offset)
			kello=local_aika.strftime("%H:%M")

			if (asema==mista_ and tyyppi=="DEPARTURE" and pysahtyy==True):
				tulostajuna[a]=("Juna: {:5} Lahtee: {} Raiteelta: {}".format(juna,kello,raide))
				break

	return (mista,mihin,tulostajuna)

def check_weather2(location):

	key=""			#API KEY

	url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location,key)
	r = requests.get(url)

	x=r.json()

	if x["cod"] != "404":

		y=x["main"]
		temp=y["temp"]
		humi=y["humidity"]
		wind_n=x["wind"]["speed"]
		wind_s=x["wind"]["deg"]

	else:
		temp="0"
		humi="0"
		wind_n="0"
		wind_s="0"

	return temp,humi,wind_n,wind_s

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

def etsi_title(a):
#	print "etsititle"
	first=" property=\"og:title\" content=\""
	last="\""

	try:
		start=a.index(first) + len(first)
		end=a.index(last, start)
		return a[start:end]
	except ValueError:
		return ""


def filter_title(title):
	mappaus={'&#034;':'"',
		'&quot;':'"',
		'http://':'meep',
		'https://':'meep',
		'&amp;':'&',
		'&#039;':'\'',
		'&#8211;':'-',
		'&#27;':'\''}

	if (title != None):
		for a,b in mappaus.iteritems():
			title=title.replace(a,b)
	else:
		title="No title found"

	return title

def avaaurl(osoite):
#	print "avaaurl"

	headers={ 'User-Agent' : 'Mozilla/5.0' }
	req=urllib2.Request(osoite,None,headers)

	try:
		f=urllib2.urlopen(req)
		ots=f.read()
		f.close

		otsikko = etsi_title(ots)
		filter = re.sub("\n\s*","",otsikko)

		return filter

	except urllib2.HTTPError,e:
		print "vamma esto",e


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


def viisaudet():
	global lista
	global vituttaa
	global utstats
	global viisaus_num

	file='viisaudet.txt'				#File which contains wisdoms

	f=open(file,'r')
	lista=f.readlines()
	f.close()
	viisaus_num=len(lista)

	vituttaa="Jos vituttaa niin mita siita suotta virtta vaantaamaan kun metsa on taynna paksu oksaisia mantyja"
	
def irc_nick_not():
#	print "Irc no user"
	time.sleep(200)
	ircconnect(host,port,name,ident,realname,chan)


def ircloop():
#	print "Ircloop"
	check=0
	msg = [None]*5
	msg[0]=".gif"
	msg[1]=".pdf"
	msg[2]=".jpg"
	msg[3]=":8000/"
	msg[4]=":80/"

	viisaudet()

	while 1:
		try:

			ircmsg = s.recv (bufsize)

			if len(ircmsg) == 0:
				break

			ircmsg = ircmsg.strip('\n\r')

#			print ircmsg

			if ircmsg.find ("belsebot :Nick/channel is temporarily unavailable") != -1:
				irc_nick_not()

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
				elif msg[3] in urls[0]:
					s.send("PRIVMSG %s :%s\r\n" % (chan,"puuuuh"))
				elif msg[4] in urls[0]:
					s.send("PRIVMSG %s :%s\r\n" % (chan,"puuuuuuh"))
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
							viesti=filter_title(viesti)
							if viesti:
								s.send("PRIVMSG %s :%s\r\n" % (chan, viesti))
							else:
								s.send("PRIVMSG %s :%s\r\n" % (chan, "No title found"))
					else:
						s.send("PRIVMSG %s :%s\r\n" % (chan, "Timeout tai joku vammainen badstatus tai muu vastaava"))

			if ircmsg.find("!viisaus") != -1:
				num=randint(0,viisaus_num-1)
				s.send("PRIVMSG %s :%s\r\n" % (chan, lista[num]))

			if ircmsg.find("!temp") != -1:
				try:
					kaupunki = ircmsg.split()
					if len(kaupunki) < 5:
						paikka="tampere"
					else:
						paikka=kaupunki[4]

					lampo,kosteus,tuuli_n,tuuli_s=check_weather2(paikka)
					saa=paikka+" lampotila:" + str(lampo) + " kosteus:" + str(kosteus) + " tuuli:" + str(tuuli_n) + " m/s suunta:" + str(tuuli_s)
					s.send("PRIVMSG %s :%s\r\n" % (chan, saa))
				except:
					print ircmsg

			if ircmsg.find("!vituttaa") != -1:
				s.send("PRIVMSG %s :%s\r\n" % (chan, vituttaa))

			if ircmsg.find("!junat") != -1:
				try:
					asema1="toijala"
					asema2="tampere"
					j_asemat = ircmsg.split()

					if len(j_asemat) < 6:
						asema1="toijala"
						asema2="tampere"
					else:
						asema1=j_asemat[4]
						asema2=j_asemat[5]
					asema1_,asema2_,j_asemat_=asemat(asema1,asema2)
					junatviesti="Junat: {} {} ".format(asema1_,asema2_)
					s.send("PRIVMSG %s :%s\r\n" % (chan, junatviesti))
					s.send("PRIVMSG %s :%s\r\n" % (chan, j_asemat_))
				except:
					s.send("PRIVMSG %s :%s\r\n" % (chan, "Joku error"))

			if ircmsg.find(":belse!") != -1:
				try:
					komento = ircmsg.split(':',2)
					if komento[2]=="!quit":
						s.send("PRIVMSG %s :%s\r\n" % (chan, "Heippa"))
						print "sammutetaan bot"
						s.close()
						break
					if komento[2]=="!reload":
						viisaudet()
						print "Viisaudet paivitetty"
				except:
					print ircmsg


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
