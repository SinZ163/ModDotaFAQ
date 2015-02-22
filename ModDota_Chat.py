import re

ID="chat"
permission=0

blackList = {
    "(http[s]?://)?([a-zA-z0-9]*\.)*reddit\.com(/.*)?" : "Voting on reddit links posted here may get you shadowbanned",
    "(http[s]?://)?([a-zA-z0-9]*\.)*redd\.it(/.*)?" : "Voting on reddit links posted here may get you shadowbanned"
}

def execute(self, name, params, channel, userdata, rank):
    pass

def __initialize__(self, Startup):
    if self.events["chat"].doesExist("ModDota_Chat"):
        self.events["chat"].removeEvent("ModDota_Chat")
    self.events["chat"].addEvent("ModDota_Chat", onPrivmsg)
    
    self.Banlist.defineGroup("ModDota")
    
def onPrivmsg(self, channels, userdata, message, currChannel):
    print("I am alive")
    for blackRegex, blackResponse in sorted(blackList.iteritems()):
        if re.search(blackRegex, message):
            self.sendMessage(currChannel, blackList[blackRegex])
        else:
            #self.sendMessage(currChannel, "\"" + message + "\" does not match the following regex: \""+blackRegex+"\"")
            pass
