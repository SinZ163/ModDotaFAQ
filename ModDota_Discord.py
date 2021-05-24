import re
import traceback

ID = "discord"
permission = 3

cmdList = ("pycalc", "convert", "utc", "workshop", "match", "prize", "valvetime")
def execute(self, name, params, channel, userdata, rank):
    pass

def __initialize__(self, Startup):
    if self.events["chat"].doesExist("Discord_privmsg"):
        self.events["chat"].removeEvent("Discord_privmsg")
    self.events["chat"].addEvent("Discord_privmsg", onPrivmsg)

def onPrivmsg(self, channels, userdata, message, currChannel):
    #print("A")
    try:
        if userdata["name"] == "D|":
            #print("B")
            #print(message)
            #print("<.(?P<rank>\d\d)(?P<name>.+?).> (?P<message>.+?)$")
            match = re.search("<.(?P<rank>\d\d)(?P<name>.+?).> (?P<message>.+?)$", message)
            #print("C")
            #print("D")
            output = match.groupdict()
            chatParams = output["message"].rstrip().split(" ")
            #print("E")
            #print(str(len(chatParams[0])))
            #print(chatParams[0][0:2])
            if chatParams[0][0] == self.cmdprefix and chatParams[0][1:] in self.commands:
                #print("F")
                if chatParams[0][1:] not in cmdList:
                    self.sendMessage(currChannel, "Unsupported command for irc bridge. Can only use "+", ".join(cmdList))
                    return
                #print("G")
                try:
                    direct_msg_support = self.commands[chatParams[0][1:]][0].privmsgEnabled
                except AttributeError:
                    direct_msg_support = False
                #print("H")

                if direct_msg_support:
                    #print("I")
                    self.commands[chatParams[0][1:]][0].execute(self, "[Discord]_"+output["name"], chatParams[1:], currChannel, ("discord", "discord"), "", chan = True)
                    #print("J")
                else:
                    #print("K")
                    self.commands[chatParams[0][1:]][0].execute(self, "[Discord]_"+output["name"], chatParams[1:], currChannel, ("discord", "discord"), "")
                    #print("L")
            elif chatParams[0][0:2] == "??":
                #print("We have a faq?")
                #must be 2
                rank = ""
                print(currChannel)
                if currChannel == "#moddota-admin":
                    rank = "@@"
                self.commands["faq"][0].execute(self, "[Discord]_"+output["name"], [chatParams[0][2:]] + chatParams[1:], currChannel, ("discord", "discord"), rank)
    except:
        print(traceback.format_exc())