import simplejson
import urllib2
import gzip
from StringIO import StringIO

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
            
    def readMsg(self, msg):
        for name, lines in self.db.iteritems():
            if msg.lower() == name.lower():
                return lines
                
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
            pass
    
    def RenderHTML(self, db):
        if self.init:
            try:
                entryText = ""
                for name, info in sorted(db.iteritems()):
                    entryText = entryText + self.templates["entry"].format(entry=(name.encode("utf-8"), ("<br/>".join(info)).encode("utf-8")))
                with open("commands/ModDota/faqSite/index.html", "w") as f:
                    f.write(self.templates["index"].format(entry=(entryText)))
            except:
                print("OHNO it didn't work, ah well")
                print(traceback.format_exc())
            
ID="faq" #this is our command identifier, so with conventional commands, this is the command name
permission=0 #Min permission required to run the command (needs to be 0 as our lowest command is 0)

#Take the symbols, and turn it into numbers (easier to do < or > with)
rankTranslate = {
    "" : 0,
    "+" : 1,
    "@" : 2,
    "@@" : 3
}
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
    try:
        if rankTranslate[rank] >= commands[params[0]]["rank"]:
            command = commands[params[0]]["function"]
            command(self, name, params, channel, userdata, rank)
        else:
            self.sendNotice(name, "You do not have permissions for this command!")
    except KeyError as e:
        #self.sendChatMessage(self.send, channel, str(e))
        self.sendChatMessage(self.send, channel, "invalid command!")
        self.sendChatMessage(self.send, channel, "see {}faq help for a list of commands".format(self.cmdprefix))

def __initialize__(self, Startup):
    if self.events["chat"].doesExist("ModDota_Faq"):
        self.events["chat"].removeEvent("ModDota_Faq")
    self.events["chat"].addEvent("ModDota_Faq", onPrivmsg)

def onPrivmsg(self, channels, userdata, message, currChannel):
    #are the first two characters equal to mainPrefix?
    if message[0:2] == mainPrefix:
        #Yes they are, lets do work!
        params = message.split(" ")
        params[0] = params[0][2:]
    else:
        #they weren't, not worth looking at it anymore
        return
    #was this in a channel, or as a privmsg
    if currChannel:
        #Channel it is
        channel = currChannel
    else:
        #Nope, was a private message
        channel = userdata["name"]
    #Ok, are they smart enough to actually run this command
    rank = self.userGetRankNum(currChannel,userdata["name"])
    #this may or may not blow up, lets be careful
    try:
        if userdata["name"] in banList:
            self.sendNotice(userdata["name"], "You have been banned from using this command.")
            return
        if rank >= commands[params[0]]["rank"]:
            #They ARE smart enough, lets try to run the command
            command = commands[params[0]]["function"]
            command(self, userdata["name"], params, channel, userdata, rank)
        else:
            #They are dumb, booo!
            self.sendNotice(userdata["name"], "You do not have permissions for this command!")
    except KeyError:
        #Ok, the command didn't exist, no biggy, act like it never happened.
        pass
        #Doing a message if someone started their message with the prefix is bad

bold = chr(2)
def command_privmsg(self, name, params, channel, userdata, rank):
    print("PRIVMSG")
    #This is where the normal command is.
    args = " ".join(params[1:])
    result = modfaq.readMsg(args)
    if result:
        for line in result:
            self.sendMessage(channel, bold+args+":"+bold+" "+line)
    
def command_notice(self, name, params, channel, userdata, rank):
    #This is where the notice command is.
    args = " ".join(params[1:])
    result = modfaq.readMsg(args)
    if result:
        for line in result:
            self.sendNotice(name, bold+args+":"+bold+" "+line)
    
def command_target(self, name, params, channel, userdata, rank):
    #This is where the target command is.
    target = params[1]
    args = " ".join(params[2:])
    result = modfaq.readMsg(args)
    if result:
        for line in result:
            self.sendMessage(channel, bold+target+":"+bold+" ("+args+") "+line)
            
def command_add(self, name, params, channel, userdata, rank):
    args = " ".join(params[1:])
    if "=" in args:
        info = args.split("=")
        modfaq.db[info[0]] = info[1].split("||")
        modfaq.SaveDB()
        self.sendMessage(channel, "Added/Modified "+info[0]+", and set it to "+info[1])
        modhtml.RenderHTML(modfaq.db)
    else:
        self.sendNotice(name, "Bad usage. use it like ??+ name=text")
    
def command_del(self, name, params, channel, userdata, rank):
    args = " ".join(params[1:])
    self.sendMessage(channel, "Deleting "+args+", used to say "+"||".join(modfaq.db[args]))
    del modfaq.db[args]
    modfaq.SaveDB()
    modhtml.RenderHTML(modfaq.db)

def debug_compile(self, name, params, channel, userdata, rank):
    modhtml.RenderHTML(modfaq.db)
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