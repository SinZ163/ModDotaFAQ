import logging
import simplejson
import string
import traceback
ID="api" #this is our command identifier, so with conventional commands, this is the command name
permission=0 #Min permission required to run the command (needs to be 0 as our lowest command is 0)

MDAPI_logger = logging.getLogger("NEMPolling")


class ModDotaAPI:
    def __init__(self):
        pass
    def ReadDump(self):
        with open("commands/ModDota/vscript-dump.txt", "r") as f:
            curClass = ""
            db = {}
            lineNum = 0
            prevLine = ""
            for line in f:
                lineMsg = line.lstrip(" ").split(" ")
                lineNum = lineNum + 1
                if lineMsg[0] == "Class":
                    #MDAPI_logger.info("This is a class, right.. :"+line)
                    #Ok, class time
                    if lineMsg[1] in db:
                        #ok, dafuq. why is this already present
                        raise ClassAlreadyExistsDontDoThisToMeException()
                    else:
                       
                        if lineMsg[1][-1:] == ",":
                            curClass = lineMsg[1][:-1]
                            db[curClass] = {"methods" : {}}
                            #Ok, it is a child class.
                            db[curClass]["base"] = lineMsg[2]
                            
                            db[curClass]["comment"] = " ".join(lineMsg[4:])
                        else:
                            curClass = lineMsg[1]
                            db[curClass] = {"methods" : {}}
                            db[curClass]["comment"] = " ".join(lineMsg[3:])
                    #Ok boys, new class
                elif "//" in line:
                    #comment, we dont care about it yet
                    #we dont want to continue, as we want the code below to run anyway
                    pass
                elif lineMsg[0] == "":
                    #blank line, boring!!
                    pass
                else:
                    #MDAPI_logger.info("This is a method, right.. : "+line)
                    #MDAPI_logger.info(lineMsg)
                    if len(lineMsg) > 1:
                        method = {
                            "return" : lineMsg[0],
                            "args" : []
                        }
                        if "()" in lineMsg[1]:
                            #no args
                            methodName = lineMsg[1][:-4]
                        else:
                            #print(lineMsg)
                            methodName = lineMsg[1][:-1]
                            i = 2
                            while lineMsg[i].rstrip() != ")":
                                method["args"].append(lineMsg[i].rstrip(","))
                                #MDAPI_logger.info(method["args"])
                                i = i + 1
                        
                        commentStart = prevLine.find("//")

                        if commentStart > -1: #meaning it exists
                            method["comment"] = prevLine[commentStart+3:]
                            
                        db[curClass]["methods"][methodName] = method
                prevLine = line
            self.db = db
            
class ModDota_Api_HTMLCompiler:
    def __init__(self):
        self.init = False
        self.community = False
        self.communityDocs = {}
        try:
            self.templates = {}
            with open("commands/ModDota/doc_template_arg.txt", "r") as f:
                self.templates["arg"] = f.read()
            
            with open("commands/ModDota/doc_template_class.txt", "r") as f:
                self.templates["class"] = f.read()
                
            with open("commands/ModDota/doc_template_class-tableofcontents.txt", "r") as f:
                self.templates["class-tableofcontents"] = f.read()
                
            with open("commands/ModDota/doc_template_function.txt", "r") as f:
                self.templates["function"] = f.read()
                
            with open("commands/ModDota/doc_template_index.txt", "r") as f:
                self.templates["index"] = f.read()
                
            with open("commands/ModDota/doc_template_tableofcontents.txt", "r") as f:
                self.templates["tableofcontents"] = f.read()
            
            self.init = True
        except:
            #fuck this, they aren't there meaning who ever setup renol failed horribly
            pass
        try:
            with open("commands/ModDota/docdb.json", "r") as f:
                self.communityDocs = simplejson.load(f)
            print(self.communityDocs)
            print("community docs loaded")
            self.community = True
        except:
            #no community for us </3
            print("OHNO it didn't work, ah well")
            print(traceback.format_exc())
    
    def GenerateClass(self, className, description=""):
        if self.community:
            if className not in self.communityDocs:
                self.communityDocs[className] = {
                    "description" : description,
                    "funcs" : {}
                }
                print("Generated class "+className)
    def GenerateFunction(self, className, funcName, description=""):
        if self.community:
            if className not in self.communityDocs:
                self.GenerateClass(className)
            if funcName not in self.communityDocs[className]:
                self.communityDocs[className]["funcs"][funcName] = {
                    "description" : description,
                    "args" : []
                }
                print("Generated function "+funcName)
    
    def RenderHTML(self, db):
        if self.init:
            print("Compiling")
            try:
                alphabetDict = list(string.ascii_lowercase)
                alphabetDict.insert(0, "death and decay")
            
            
                tableOfContents = ""
                for Class in sorted(db):
                    tableOfContents = tableOfContents + self.templates["tableofcontents"].format(name=(Class))
                    
                contents=""
                classInfo = []
                for Class, ClassInfo in sorted(db.iteritems()):
                    communityClass = False
                    #print("Do we have this class defined")
                    if self.community:
                        if Class in self.communityDocs:
                            communityClass = True
                            #print("Ok, in theory we should be fine")
                    
                    classTableOfContents = ""
                    for Func in sorted(ClassInfo["methods"]):
                        classTableOfContents = classTableOfContents + self.templates["class-tableofcontents"].format(className=(Class), func=(Func))
                        
                    functionText = ""
                    for Func, FuncInfo in sorted(ClassInfo["methods"].iteritems()):
                        communityFunc = False
                        if communityClass == True:
                            #print("Do we have this func defined")
                            if Func in self.communityDocs[Class]["funcs"]:
                                communityFunc = True
                                #print("Ok, in theory we should be double fine")
                                
                        #print(FuncInfo)
                        if "comment" not in FuncInfo:
                            FuncInfo["comment"] = "Valve didn't give us a description, sucks.."
                            
                        communityArg = False
                        if communityClass and communityFunc:
                            if len(self.communityDocs[Class]["funcs"][Func]["args"]) > 0:
                                communityArg = True
                            else:
                                print("Not enough args")
                        i = 0                      
                        newArgs = []
                        for arg in FuncInfo["args"]:
                            #print(FuncInfo)
                            i = i + 1
                            #print(communityClass, communityFunc)
                            if communityArg:
                                if len(self.communityDocs[Class]["funcs"][Func]["args"]) >= i:
                                #print(self.communityDocs[Class]["funcs"][Func]["args"][i-1])
                                    if self.communityDocs[Class]["funcs"][Func]["args"][i-1]:
                                        newArgs.append(arg + " " + self.communityDocs[Class]["funcs"][Func]["args"][i-1])
                                        continue
                                        
                            newArgs.append(arg + " " + alphabetDict[i])
                        communityDescText = " "
                        if communityFunc:
                            communityDescText = self.communityDocs[Class]["funcs"][Func]["description"]
                        functionText = functionText + self.templates["function"].format(className=(Class), func=(Func), entry=(FuncInfo), args=(", ".join(newArgs)), communityDesc=(communityDescText), arg=("This is coming soon!"))
                    
                        del Func, FuncInfo
                        
                    if "base" not in ClassInfo:
                        ClassInfo["base"] = "n/a"
                        
                    desc = " "
                    if communityClass:
                        desc = self.communityDocs[Class]["description"]
                    classInfo.append(self.templates["class"].format(name=(Class),entry=ClassInfo, classtableofcontents=(classTableOfContents), function=(functionText), description=(desc) ))
                    
                    del Class, ClassInfo
                contents = "<hr class=\"line-class-seperate\">\r\n    ".join(classInfo)
                with open("commands/ModDota/docSite/index.html", "w") as f:
                    f.write(self.templates["index"].format(tableofcontents=(tableOfContents), contents=(contents)))
            except:
                print("OHNO it didn't work, ah well")
                print(traceback.format_exc())
            try:
                if self.community:
                    with open("commands/ModDota/docdb.json", "w") as f:
                        simplejson.dump(self.communityDocs, fp = f, sort_keys=True, indent=4 * ' ', encoding = "utf-8")
            except:
                print("uhh, wat")
            
modDotaAPI = ModDotaAPI()
modhtml = ModDota_Api_HTMLCompiler()

mainPrefix = "@"

#called when the bot has loaded everything and is connected
def __initialize__(self, Startup):
    modDotaAPI.ReadDump()
    with open("commands/ModDota/vscript-dump.json", "w") as f:
        f.write(simplejson.dumps(modDotaAPI.db, sort_keys=True, indent=4 * ' '))
        
    if self.events["chat"].doesExist("ModDota_Docs"):
        self.events["chat"].removeEvent("ModDota_Docs")
    self.events["chat"].addEvent("ModDota_Docs", onPrivmsg)

def onPrivmsg(self, channels, userdata, message, currChannel):
    print("Hai")
    #are the first two characters equal to mainPrefix?
    if message[0:1] == mainPrefix:
        #Yes they are, lets do work!
        params = message.split(" ")
        params[0] = params[0][1:]
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
        """if userdata["name"] in banList:
            self.sendNotice(userdata["name"], "You have been banned from using this command.")
            return"""
        cmd = False
        if params[0] in aliases:
            print("using alias")
            cmd = aliases[params[0]]
        elif params[0] in commands:
            print("using actual command")
            cmd = params[0]
            
        if cmd:
            if rank >= commands[cmd]["rank"]:
                #They ARE smart enough, lets try to run the command
                command = commands[cmd]["function"]
                command(self, userdata["name"], params[1:], channel, userdata, rank)
            else:
                #They are dumb, booo!
                self.sendNotice(userdata["name"], "You do not have permissions for this command!")
        else:
            print("Failwhale typo")
    except KeyError:
        print(traceback.format_exc())
        #Ok, the command didn't exist, no biggy, act like it never happened.
        #Doing a message if someone started their message with the prefix is bad
        
#the command entry point from '=api" or something
def execute(self, name, params, channel, userdata, rank):
    msg = " ".join(params)
    methods = []
    output = channel
    for Class, ClassInfo in modDotaAPI.db.iteritems():
        for MethodName, MethodInfo in ClassInfo["methods"].iteritems():
            #print(MethodName)
            if msg.lower() in MethodName.lower():
                #MDAPI_logger.info("Found a method, "+MethodName)
                methods.append((Class, MethodName))
    if len(methods) == 0:
        self.sendMessage(channel, "No results found.")
    if len(methods) > 5:
        #pm it
        if len(methods) > 20:
            self.sendMessage(channel, "Too many functions matched ("+str(len(methods))+"). Please refine your search.")
            return
        else:
            output = name
            self.sendMessage(channel, "Too many functions matched ("+str(len(methods))+"). replying privately.")
    colBold = chr(2)
    colBlue = chr(3)+"02"
    colEnd = chr(3)
    for method in methods:
        args = ""
        if len(modDotaAPI.db[method[0]]["methods"][method[1]]["args"]) > 0:
            sep = colEnd + ", " + colBlue
            args = " " + colBlue + sep.join(modDotaAPI.db[method[0]]["methods"][method[1]]["args"]) + colEnd +  " "
            
        comment = ""
        if "comment" in modDotaAPI.db[method[0]]["methods"][method[1]]:
            comment = " -- "+modDotaAPI.db[method[0]]["methods"][method[1]]["comment"]
        self.sendMessage(output, "["+method[0]+"] "+modDotaAPI.db[method[0]]["methods"][method[1]]["return"] + " " + method[1] + colBold+"(" + colBold + args + colBold+")" + colBold + comment)

def command_class(self, name, params, channel, userdata, rank):
    if len(params) > 1:
        if modhtml.community:
            if params[0] in modhtml.communityDocs:
                print("changing description rather than defining class")
                modhtml.communityDocs[params[0]]["description"] = " ".join(params[1:])
                self.sendMessage(channel, "Set the description of "+params[0]+" and set it to "+" ".join(params[1:]))
                modhtml.RenderHTML(modDotaAPI.db)
            else:
                modhtml.GenerateClass(params[0], description=" ".join(params[1:]))

                self.sendMessage(channel, "Defined "+params[0]+", and set the description to "+" ".join(params[1:]))
                modhtml.RenderHTML(modDotaAPI.db)
        else:
            self.sendMessage(channel, "Sorry, community documentation is out of service at the moment")
    else:
        self.sendMessage(channel, "ERROR: Not enough arguments")
    
def command_function(self, name, params, channel, userdata, rank):
    if len(params) >= 2:
        if len(params) == 2:
            params.append(" ")
        if modhtml.community:
            if params[1] in modhtml.communityDocs[params[0]]["funcs"]:
                print("changing description rather than defining class")
                modhtml.communityDocs[params[0]]["funcs"][params[1]]["description"] = " ".join(params[2:])
                self.sendMessage(channel, "Set the description of "+params[1]+" and set it to "+" ".join(params[2:]))
                modhtml.RenderHTML(modDotaAPI.db)
            else:
                modhtml.GenerateFunction(params[0], params[1], description=" ".join(params[2:]))
                
                self.sendMessage(channel, "Defined "+params[1]+", and set the description to "+" ".join(params[2:]))
                modhtml.RenderHTML(modDotaAPI.db)      
        else:
            self.sendMessage(channel, "Sorry, community documentation is out of service at the moment")
    else:
        self.sendMessage(channel, "ERROR: Not enough arguments")
        
def command_argument(self, name, params, channel, userdata, rank):
    if len(params) > 2:
        if modhtml.community:
            if params[0] not in modhtml.communityDocs or params[1] not in modhtml.communityDocs[params[0]]["funcs"]:
                modhtml.GenerateFunction(params[0], params[1])
                
            newparams = params[2:]
            i = 0
            for param in newparams:
                if param == "*nope*":
                    newparams[i] = False
                i = i + 1
            modhtml.communityDocs[params[0]]["funcs"][params[1]]["args"] = newparams
            self.sendMessage(channel, "Set the arguments of "+params[1]+" to \""+", ".join(params[2:])+"\"")
            modhtml.RenderHTML(modDotaAPI.db)
        else:
            self.sendMessage(channel, "Sorry, community documentation is out of service at the moment")
    else:
        self.sendMessage(channel, "ERROR: Not enough arguments")
    
def debug_compile(self, name, params, channel, userdata, rank):
    print("Debug compiling")
    modhtml.RenderHTML(modDotaAPI.db)
    self.sendMessage(channel, "Done.")

aliases = {
    "arguments" : "argument"
}    
commands = {
    "class" : {
        "function" : command_class, #The function to call
        "rank" : 1, #What is the min rank to use it
        #Note, everything below here is just for the help command
        "help" : "Defines a class with its description",        
        "args" : [
            {
                "name" : "class",
                "description" : "The class that gets this new description",
                "required" : True
            },
            {
                "name" : "description",
                "description" : "The community description that will be assigned to this class",
                "required" : True
            }
        ]
    },
    "function" : {
        "function" : command_function, #The function to call
        "rank" : 1, #What is the min rank to use it
        #Note, everything below here is just for the help command
        "help" : "Defines a function with its description",
        "args" : [
            {
                "name" : "class",
                "description" : "The class that this function lives in",
                "required" : True
            },
            {
                "name" : "function",
                "description" : "the function that gets this new description",
                "required" : True
            },
            {
                "name" : "description",
                "description" : "The community description that will be assigned to this function",
                "required" : True
            }
        ]
    },
    "argument" : {
        "function" : command_argument, #The function to call
        "rank" : 1, #What is the min rank to use it
        #Note, everything below here is just for the help command
        "help" : "Defines the community arguments for this function, use the keyword \"*nope*\" to skip that argument",
        "args" : [
            {
                "name" : "class",
                "description" : "The class that this function lives in",
                "required" : True
            },
            {
                "name" : "function",
                "description" : "the function that gets this new argument name list",
                "required" : True
            },
            {
                "name" : "arguments",
                "description" : "the argument names that will be given to this function",
                "required" : True
            }
        ]
    },
    "compile" : {
        "function" : debug_compile,
        "rank" : 3,
        "help" : "Manually compiles the html webpage"
    },
}

