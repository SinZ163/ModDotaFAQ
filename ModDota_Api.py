import logging
import simplejson

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
                            methodName = lineMsg[1][:-3]
                        else:
                            methodName = lineMsg[1][:-1]
                            i = 2
                            while lineMsg[i] != ")\n":
                                method["args"].append(lineMsg[i].rstrip(","))
                                #MDAPI_logger.info(method["args"])
                                i = i + 1
                        
                        commentStart = prevLine.find("//")

                        if commentStart > -1: #meaning it exists
                            method["comment"] = prevLine[commentStart+3:]
                            
                        db[curClass]["methods"][methodName] = method
                prevLine = line
            self.db = db
            
modDotaAPI = ModDotaAPI()

#called when the bot has loaded everything and is connected
def __initialize__(self, Startup):
    modDotaAPI.ReadDump()
    with open("commands/ModDota/vscript-dump.json", "w") as f:
        f.write(simplejson.dumps(modDotaAPI.db, sort_keys=True, indent=4 * ' '))

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
