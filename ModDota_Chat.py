import re
import random
import os
from datetime import datetime
import codecs

ID="chat"
permission=0

blackList = {
    #"(http[s]?://)?([a-zA-z0-9]*\.)*(?<!np\.)(reddit\.com|redd\.it)(/.*)?" : u"+report {name} Use np.reddit.com links in the future!"
}
kickList = {
}
class ModDota_Logger():
    def __init__(self):
        self.__create_directory__("commands/ModDota/Logs")
    def Log(self, channel, message):
        with codecs.open("commands/ModDota/Logs/{channel}.log".format(channel=channel), "a", encoding="utf-8") as f:
            f.write(u"[{timestamp}] {message}\r\n".format(timestamp=datetime.now().strftime('%y:%m:%d_%H:%M:%S'), message=message))
    def LogMessage(self, channel, user, message):
        #Step 1: is it a message or a privmsg
        if channel == False:
            #it was a privmsg
            return
        #Step 2: is it a CTCP Action or a message
        if message.startswith(chr(1)+"ACTION "):
            #CTCP Action
            trimmedMessage = message[len(chr(1)+"ACTION "):]
            self.Log(channel, u"* {user} {message}".format(user=user,message=trimmedMessage))
        else:
            #Message
            self.Log(channel, u"<{user}> {message}".format(user=user,message=message))
    def LogJoin(self, channel, name, ident, host):
        self.Log(channel, u"! {name} has joined! ({ident}!{host})".format(name=name,ident=ident,host=host))
    def LogPart(self, channel, user, message):
        self.Log(channel, u"! {user} has parted! ({message})".format(user=user,message=message))
    def LogQuit(self, channels, user, message):
        for channel in channels:
            self.Log(channel, u"! {user} has quit! ({message})".format(user=user,message=message))
    def LogKick(self, channel, user, message):
        self.Log(channel, u"! {user} has been kicked! (!{message})".format(user=user,message=message))
    def LogBan(self, channel, user, message):
        self.Log(channel, u"! {user} has been banned! (!{message})".format(user=user,message=message))
    def LogChange(self, channels, user, newUser):
        for channel in channels:
            self.Log(channel, u"! {user} is now known as: {newUser}".format(user=user,newUser=newUser))

    #Shamelessly stolen from Renol's logging manager by Yoshi2
    def __create_directory__(self, dirpath):
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
            print "created dir"
        elif not os.path.isdir(dirpath):
            raise RuntimeError("A file with the path {0} already exists, please delete or rename it.".format(dirpath))
        else:
            print "no dir needs to be created"
            pass

md_logger = ModDota_Logger()

def execute(self, name, params, channel, userdata, rank):
    pass

def __initialize__(self, Startup):
    if self.events["chat"].doesExist("ModDota_Chat_privmsg"):
        self.events["channeljoin"].removeEvent("ModDota_Chat_join")
        self.events["channelpart"].removeEvent("ModDota_Chat_part")
        self.events["channelkick"].removeEvent("ModDota_Chat_kick")
        self.events["nickchange"].removeEvent("ModDota_Chat_change")
        self.events["userquit"].removeEvent("ModDota_Chat_quit")
        self.events["chat"].removeEvent("ModDota_Chat_privmsg")

    self.events["channeljoin"].addEvent("ModDota_Chat_join", onJoin)
    self.events["channelpart"].addEvent("ModDota_Chat_part", onPart)
    self.events["channelkick"].addEvent("ModDota_Chat_kick", onKick)
    self.events["nickchange"].addEvent("ModDota_Chat_change", onNickChange)
    self.events["userquit"].addEvent("ModDota_Chat_quit", onQuit)
    self.events["chat"].addEvent("ModDota_Chat_privmsg", onPrivmsg)

#The following events are only for logging
def onJoin(self, channels, name, ident, host, channel):
    md_logger.LogJoin(channel, name, ident, host)

def onNickChange(self, channels, name, newName, ident, host, affectedChannels):
    md_logger.LogChange(affectedChannels, name, newName)

def onQuit(self, channels, name, ident, host, quitReason):
    #Time to make affectedChannels
    affectedChannels = []
    for chan in self.channelData:
        for i in range(len(self.channelData[chan]["Userlist"])):
            user, pref = self.channelData[chan]["Userlist"][i]
            if user == name:
                affectedChannels.append(chan)
                break
    md_logger.LogQuit(affectedChannels, name, quitReason)

def onPart(self, channels, name, ident, host, channel):
    #0.o
    partReason = ""
    md_logger.LogPart(channel, name, partReason)

def onKick(self, channels, name, channel, kickReason):
    md_logger.LogKick(channel, name, kickReason)
#Doesn't exist in Renol yet </3
#def onBan():
#    pass
#End only logging

def onPrivmsg(self, channels, userdata, message, currChannel):
    #First up, put it in chat logs
    md_logger.LogMessage(currChannel, userdata["name"], message)

    #print("I am alive")
    for blackRegex, blackResponse in sorted(blackList.iteritems()):
        if re.search(blackRegex, message):
            if userdata["name"] == "DB":
                match = re.search("<.(?P<rank>\d\d)(?P<name>.+?).> (?P<message>.+?)$", message)
                userdata = match.groupdict()
            self.sendMessage(currChannel, blackList[blackRegex].format(**userdata))
        else:
            #self.sendMessage(currChannel, "\"" + message + "\" does not match the following regex: \""+blackRegex+"\"")
            pass
    for kickRegex, kickResponse in sorted(kickList.iteritems()):
        if re.search(kickRegex, message):
            kickEntry = kickList[kickRegex]
            randomNumber = random.random()
            if randomNumber<= kickEntry["chance"]:
                msg = u"KICK {chan} {person} :{message}".format(chan=currChannel, message=kickEntry["message"], person=userdata["name"])
                self.send(msg)
                print(msg)
            else:
                print(str(randomNumber)+" was less than "+str(kickEntry["chance"]))
               # self.sendNotice("SinZ", str(randomNumber)+" wasn't less than "+str(kickEntry["chance"]))