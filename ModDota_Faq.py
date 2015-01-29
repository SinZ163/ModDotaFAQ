import simplejson
import cgi
import traceback

from string import strip as string_strip

class ModDota_Faq:
    def __init__(self):
        self.ReadDB()

    def ReadDB(self):
        with open("commands/ModDota/faqdb.json", "r") as f:
            jsonres = simplejson.load(f, encoding = "utf-8", strict = False)
            #jsonres = simplejson.loads(f.read().encode("utf-8"), strict = False )
            self.db = jsonres
        
    def SaveDB(self):
        with open("commands/ModDota/faqdb.json", "w") as f:
            simplejson.dump(self.db, fp = f, sort_keys=True, indent=4 * ' ', encoding = "utf-8")
            #f.write(simplejson.dumps(self.db, sort_keys=True, indent=4 * ' ').encode("utf-8"))
            
    def readMsg(self, topic):
        topic = topic.lower()
        if topic in self.db:
            messages = self.db[topic][1:] 
            return self.db[topic][0], messages
        else:
            return None, None
    
    def setMsg(self, topic, msg):
        topicLower = topic.lower()
        
        if topicLower in self.db:
            realname = self.db[topicLower][0]
            msg.insert(0, realname) # The first entry will be the real case of the topic
            
            self.db[topicLower] = msg
            return True
        else:
            return None
    
    def addMsg(self, topic, msg):
        assert isinstance(msg, list)
        topicLower = topic.lower()
        realname = topic
        
        msg.insert(0, realname)
        
        self.db[topicLower] = msg
    
    def delMsg(self, topic):
        topicLower = topic.lower()
        
        del self.db[topicLower]
    
    def topicExists(self, topic):
        return self.db[topic.lower()]
                
class ModDota_Faq_HTMLCompiler:
    def __init__(self):
        self.init = False
        try:
            self.templates = {}
            with open("commands/ModDota/faq_template_index.txt", "r") as f:
                self.templates["index"] = f.read()
            with open("commands/ModDota/faq_template_entry.txt", "r") as f:
                self.templates["entry"] = f.read()
            self.init = True
        except:
            #fuck this, they aren't there meaning who ever setup renol failed horribly
            print "ModDotaFAQ ERROR appeared!"
            traceback.print_exc()
    
    def RenderHTML(self, db):
        if self.init:
            try:
                entryText = ""
                for name, info in sorted(db.iteritems()):
                    realName = db[name][0]
                    info = db[name][1:]
                    
                    info = "||".join(info)
                    info = cgi.escape(info, quote=True)
                    info = info.replace("||", "<br/>")
                    
                    entryText = entryText + self.templates["entry"].format(entry=(realName.encode("utf-8"), info.encode("utf-8")))
                    
                with open("commands/ModDota/faqSite/index.html", "w") as f:
                    f.write(self.templates["index"].format(entry=(entryText)))
            except:
                print("OHNO it didn't work, ah well")
                print(traceback.format_exc())
            
ID="faq" #this is our command identifier, so with conventional commands, this is the command name
permission=0 #Min permission required to run the command (needs to be 0 as our lowest command is 0)

#Take the numbers, and turn it back to words
nameTranslate = [
    "Guest",
    "Voice",
    "Operator",
    "Bot Admin"
]
#Nicknames in this list cannot run the commands, even if they have permission
banList = [
]
#What is our homemade prefix?
mainPrefix = "??"

modfaq = ModDota_Faq()
modhtml = ModDota_Faq_HTMLCompiler()

#the command entry point from '=faq" or something
def execute(self, name, params, channel, userdata, rank):
    if len(params) == 0:
        self.sendChatMessage(self.send, channel, "See {}faq help for a list of commands".format(self.cmdprefix))
        return
    
    try:
        ident, host = userdata
        
        banned, info = self.Banlist.checkBan(name, ident, host, groupName = "ModDota")
        if banned:
            self.sendNotice(name, "You are banned from using this command.")
            return
        
        if self.rankconvert[rank] >= commands[params[0]]["rank"]:
            command = commands[params[0]]["function"]
            command(self, name, params, channel, userdata, rank)
        else:
            self.sendNotice(name, "You do not have permissions for this command!")
    except KeyError as e:
        #self.sendChatMessage(self.send, channel, str(e))
        self.sendChatMessage(self.send, channel, "Invalid command.")
        self.sendChatMessage(self.send, channel, "See {}faq help for a list of commands".format(self.cmdprefix))

def __initialize__(self, Startup):
    if self.events["chat"].doesExist("ModDota_Faq"):
        self.events["chat"].removeEvent("ModDota_Faq")
    self.events["chat"].addEvent("ModDota_Faq", onPrivmsg)
    
    self.Banlist.defineGroup("ModDota")

def onPrivmsg(self, channels, userdata, message, currChannel):
    # Are the first two characters equal to mainPrefix?
    if message[0:2] == mainPrefix:
        # Yes they are, lets do work!
        params = message.split(" ")
        params[0] = params[0][2:]
    else:
        # They weren't, not worth looking at it anymore.
        return

    if currChannel:
        # Message was sent in a channel
        channel = currChannel
    else:
        # Nope, was a private message
        channel = userdata["name"]
    # Ok, are they smart enough to actually run this command?
    rank = self.userGetRankNum(currChannel,userdata["name"])
    
    # This may or may not blow up, lets be careful.
    try:
        globalbanned, globalinfo = self.Banlist.checkBan(userdata["name"], userdata["ident"], 
                                                         userdata["host"])
        banned, info = self.Banlist.checkBan(userdata["name"], userdata["ident"], 
                                             userdata["host"], groupName = "ModDota")
        if banned or globalbanned:
            self.sendNotice(userdata["name"], "You are banned from using this command.")
            return
        if rank >= commands[params[0]]["rank"]:
            # They ARE smart enough, lets try to run the command.
            command = commands[params[0]]["function"]
            command(self, userdata["name"], params, channel, userdata, rank)
        else:
            # They are dumb, booo!
            self.sendNotice(userdata["name"], "You do not have permissions for this command!")
    except KeyError:
        # Ok, the command didn't exist, no biggy, act like it never happened.
        pass
        # Sending a message if someone started their message with the prefix is bad.

bold = chr(2)
def command_privmsg(self, name, params, channel, userdata, rank):
    print("PRIVMSG")
    # This is triggered when using ?? <topic>
    # Sends a message in the channel.
    args = " ".join(params[1:]).strip()
    realname, lines = modfaq.readMsg(args)
    
    if realname != None:
        for line in lines:
            self.sendMessage(channel, u"{0}{1}:{0} {2}".format(bold, realname, line))
    else:
        self.sendNotice(name, u"No such topic with the name '{0}'.".format(args))
    
def command_notice(self, name, params, channel, userdata, rank):
    # This is triggered when using ??< <topic>
    # Sends a notice to the user.
    args = " ".join(params[1:]).strip()
    realname, lines = modfaq.readMsg(args)
    
    if realname != None:
        for line in lines:
            self.sendNotice(name, u"{0}{1}:{0} {2}".format(bold, realname, line))
    else:
        self.sendNotice(name, u"No such topic with the name '{0}'.".format(args))
    
def command_target(self, name, params, channel, userdata, rank):
    #This is triggered when using ??> <username> <topic>
    # Sends a message in the channel, but puts the name of the
    # target user at the start.
    
    params.pop(0) # removing the command sign
    
    # We need to remove any leading empty strings before the first
    # TRUE parameter (one that is not an empty string).
    # Those empty strings appear due to splitting the initial
    # chat message string at whitespace, resulting in empty strings
    # if two or more white spaces come after another.
    for i in range(len(params)):
        if len(params[0]) > 0:
            break
        else:
            params.pop(0)
    if len(params) < 2:
        self.sendNotice(name, "Not enough parameters")
        return
    target = params[0].strip()
    args = (" ".join(params[1:])).strip()
    
    realname, lines = modfaq.readMsg(args)
    
    if realname != None:
        for line in lines:
            self.sendMessage(channel, u"{0}{1}:{0} ({2}) {3}".format(bold, target, realname, line))
    else:
        self.sendNotice(name, u"No such topic with the name '{0}'.".format(args))
            
def command_add(self, name, params, channel, userdata, rank):
    args = " ".join(params[1:]).strip()
    
    if "=" in args:
        # We need to remove the leading and trailing whitespaces.
        # This way, '??+ foo=bar' is the same as '??+ foo = bar'
        info = map(string_strip, args.split("=", 1))
        
        topicName = info[0]
        topicNameLower = topicName.lower()
        
        # We also need to remove the leading and trailing whitespaces from
        # each line, signaled by ||. map() lets us do it in one line.
        topicContent = map(string_strip, info[1].split("||"))
        
        if topicNameLower in modfaq.db:
            modfaq.setMsg(topicNameLower, topicContent)
            realname = modfaq.db[topicNameLower][0]
            
            
            self.sendMessage(channel, u"Modified '{0}' and set it to '{1}'".format(realname, info[1]))
        else:
            modfaq.addMsg(topicName, topicContent)
            
            self.sendMessage(channel, u"Added '{0}' and set it to '{1}'".format(topicName, info[1]))
        
        modfaq.SaveDB()
        modhtml.RenderHTML(modfaq.db)
    else:
        self.sendNotice(name, "Incorrect syntax. Use the command like this: ??+ name=text")
    
def command_del(self, name, params, channel, userdata, rank):
    args = " ".join(params[1:]).strip()
    topic = args.lower()
    
    if topic in modfaq.db:
        realname = modfaq.db[topic][0]
        self.sendMessage(channel, u"Deleting '{0}', used to say '{1}'".format(realname, u"||".join(modfaq.db[topic][1:])))
        
        modfaq.delMsg(topic)
        modfaq.SaveDB()
        modhtml.RenderHTML(modfaq.db)
    else:
        self.sendNotice(name, u"No such topic with the name '{0}'.".format(args))

def debug_compile(self, name, params, channel, userdata, rank):
    modhtml.RenderHTML(modfaq.db)
    self.sendNotice(name, "Done.")
    
    
    
    
    
#This is the database for all the commands
commands = {
    ">" : {
        "function" : command_target, #The function to call
        "rank" : 0, #What is the min rank to use it
        #Note, everything below here is just for the help command
        "help" : "Says the FAQ you are after, but prefixed with your targets name to bring attention to it",
        "args" : [
            {
                "name" : "target",
                "description" : "the name to prefix the faq qith",
                "required" : True
            },
            {
                "name" : "faq",
                "description" : "the faq you want to show",
                "required" : True
            }
        ]
    },
    "<" : {
        "function" : command_notice, #The function to call
        "rank" : 0, #What is the min rank to use it
        #Note, everything below here is just for the help command
        "help" : "Says the FAQ you are after, but only you will see it.",
        "args" : [
            {
                "name" : "faq",
                "description" : "the faq you want to show",
                "required" : True
            }
        ]
    },
    "" : {
        "function" : command_privmsg, #The function to call
        "rank" : 0, #What is the min rank to use it
        #Note, everything below here is just for the help command
        "help" : "Says the FAQ you are after in the channel.",
        "args" : [
            {
                "name" : "faq",
                "description" : "the faq you want to show",
                "required" : True
            }
        ]
    },
    "+" : {
        "function" : command_add,
        "rank" : 1,
        "help" : "Adds the FAQ to the database.",
        "args" : [
            {
                "name" : "name",
                "description" : "what faq to modify/add",
                "required" : True
            },{
                "name" : "info",
                "description" : "what the faq should say",
                "required" : True
            }
        ]
    },
    "-" : {
        "function" : command_del,
        "rank" : 1,
        "help" : "Deletes the FAQ from the database.",
        "args" : [
            {
                "name" : "faq",
                "description" : "the faq to delete",
                "required" : True
            }
        ]
    },
    "compile" : {
        "function" : debug_compile,
        "rank" : 3,
        "help" : "Manually compiles the html webpage"
    }
}
