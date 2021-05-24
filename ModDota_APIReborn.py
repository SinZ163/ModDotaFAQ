import simplejson
import string
import time
import traceback
import logging
import requests
ID="api" #this is our command identifier, so with conventional commands, this is the command name
permission=0 #Min permission required to run the command (needs to be 0 as our lowest command is 0)

import collections

def update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

class ModDotaAPI:
    def __init__(self):
        self.requests_session = requests.Session()
        self.requests_session.headers = {
            'User-agent': 'ModDota_API/1.X (+http://github.com/SinZ163/ModDotaFAQ)'
        }
        self.ReadDump()
    def fetch_page(self, url, timeout=10, decode_json=True):
        request = self.requests_session.get(url, timeout=timeout)
        if decode_json:
            return request.json()
        else:
            return request.text
    def ReadDump(self):
        serverInfo = self.fetch_page("https://raw.githubusercontent.com/ModDota/API/master/_data/lua_server.json")
        #serverInfo = self.fetch_page("https://raw.githubusercontent.com/SinZ163/TestTracking/master/lua_server.json")
        communityInfo = self.fetch_page("https://raw.githubusercontent.com/ModDota/API/master/_data/override_lua_server.json")
        self.lua_server = serverInfo.copy()
        self.lua_server = update(self.lua_server, communityInfo)
        #TODO: add community db here and inject into lua_server

MDAPI_logger = logging.getLogger("MDAPI_Reborn")
modDotaAPI = ModDotaAPI()

#called when the bot has loaded everything and is connected
def __initialize__(self, Startup):
    pass
#the command entry point from '=api" or something
def execute(self, name, params, channel, userdata, rank):
    msg = " ".join(params)
    functions = []
    output = channel
    #TODO: add logic to figure out which dump we want
    for Class, ClassInfo in modDotaAPI.lua_server.iteritems():
        for FunctionName, FunctionInfo in ClassInfo["functions"].iteritems():
            #print(FunctionName)
            if msg.lower() in FunctionName.lower():
                MDAPI_logger.info("Found a method, "+FunctionName)
                functions.append((Class, FunctionName))
    if len(functions) == 0:
        self.sendMessage(channel, "No results found.")
    if len(functions) > 5:
        #pm it
        if name == "DB" or len(functions) > 20:
            self.sendMessage(channel, "Too many functions matched ("+str(len(functions))+"). Please refine your search.")
            return
        else:
            output = name
            self.sendMessage(channel, "Too many functions matched ("+str(len(functions))+"). replying privately.")
    colBold = chr(2)
    colItalics = chr(29)
    colGreen = chr(3)+"03"
    colBlue = chr(3)+"02"
    colBrown = chr(3)+"07"
    colEnd = chr(3)

    for function in functions:
        className = function[0]
        functionName = function[1]
        functionInfo = modDotaAPI.lua_server[className]["functions"][functionName]
        argInfo = ""
        description = ""
        if "args" in functionInfo:
            if len(functionInfo["args"]) > 0:
                #We have argument info
                for index, arg in enumerate(functionInfo["args"]):
                    if index > 0:
                        argInfo = argInfo + ", "
                    if "arg_names" in functionInfo:
                        if len(functionInfo["arg_names"]) > 0:
                            #we have argument info with named variables
                            argInfo = argInfo + u"{nullable}{colBrown}{argType}{colBrown}{nullable} {colBlue}{argName}{colEnd}".format(
                                colBrown = colBrown,
                                colBlue = colBlue,
                                colEnd = colEnd,
                                argType = arg,
                                argName = functionInfo["arg_names"][index],
                                nullable = colItalics if "?" in arg else ""
                            )
                            continue
                    argInfo = argInfo + u"{nullable}{colBrown}{argType}{colEnd}{nullable}".format(
                        colBrown = colBrown,
                        colEnd = colEnd,
                        argType = arg,
                        nullable = colItalics if "?" in arg else ""
                    )
        if argInfo != "":
            argInfo = " " + argInfo + " "
        if "description" in functionInfo:
            description = "{colGreen} -- {description}{colEnd}".format(
                description = functionInfo["description"],
                colGreen = colGreen,
                colEnd = colEnd
            )

        #self.sendMessage(output, "["+method[0]+"] "+modDotaAPI.db[method[0]]["methods"][method[1]]["return"] + " " + method[1] + colBold+"(" + colBold + msg + colBold+")" + colBold + comment)
        self.sendMessage(output, "[{colBlue}{className}{colEnd}] {colBrown}{returnType}{colEnd} {name}{bold}({bold}{argInfo}{bold}){bold} {description}".format(
            bold = colBold,
            italic = colItalics,
            colBlue = colBlue,
            colBrown = colBrown,
            colEnd = colEnd,
            className = className,
            name = functionName,
            returnType = functionInfo["return"],
            argInfo = argInfo,
            description = description
        ))
