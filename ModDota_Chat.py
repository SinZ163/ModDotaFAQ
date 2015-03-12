import re
import random

ID="chat"
permission=0

blackList = {
    "(http[s]?://)?([a-zA-z0-9]*\.)*(?<!np\.)(reddit\.com|redd\.it)(/.*)?" : "Posting reddit links will get you shadowbanned"
}
kickList = {
}

def execute(self, name, params, channel, userdata, rank):
    pass

def __initialize__(self, Startup):
    if self.events["chat"].doesExist("ModDota_Chat"):
        self.events["chat"].removeEvent("ModDota_Chat")
    self.events["chat"].addEvent("ModDota_Chat", onPrivmsg)
    
    self.Banlist.defineGroup("ModDota")
    
def onPrivmsg(self, channels, userdata, message, currChannel):
    #print("I am alive")
    for blackRegex, blackResponse in sorted(blackList.iteritems()):
        if re.search(blackRegex, message):
            self.sendMessage(currChannel, blackList[blackRegex])
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