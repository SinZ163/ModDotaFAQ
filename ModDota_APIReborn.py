import string
import time
import traceback
import logging
import requests
ID="api" #this is our command identifier, so with conventional commands, this is the command name
permission=0 #Min permission required to run the command (needs to be 0 as our lowest command is 0)

colBold = chr(2)
colBlue = chr(3)+"02"
colGreen = chr(3)+"03"
colRed = chr(3)+"04"
colBrown = chr(3)+"07"
colEnd = chr(3)

def formatArgumentName(name):
    return colBlue + name + colEnd

def formatFunctionArgument(arg):
    return formatArgumentName(arg["name"]) + ": " + formatTypes(arg["types"])

def formatFunctionArguments(args):
    return ", ".join(map(formatFunctionArgument, args))

def formatType(type):
    if isinstance(type, basestring):
        return colBrown + type + colEnd
    elif "array" in type:
        return "[" + formatTypes(type["array"]) + "]"
    else:
        return "{bold}({bold}{args}{bold}){bold} => {returns}".format(
            bold = colBold,
            args = formatFunctionArguments(type["args"]),
            returns = formatTypes(type["returns"])
        )

def formatTypes(types):
    return " | ".join(map(formatType, types))

def formatAvailability(availability):
    return "[{colBlue}{availability}{colEnd}] ".format(
        colBlue = colBlue,
        availability = availability.capitalize(),
        colEnd = colEnd,
    )

def formatDescription(lines):
    description = ""

    for line in lines:
        description += "\n    " if len(lines) > 1 else " "
        description += "{colGreen}-- {line}{colEnd}".format(
            colGreen = colGreen,
            line = line,
            colEnd = colEnd,
        )

    return description

def formatCallSignature(function):
    return "{bold}({bold}{args}{bold}){bold}: {returns}".format(
        bold = colBold,
        args = formatFunctionArguments(function["args"]),
        returns = formatTypes(function["returns"]),
    )

def formatFunction(function, scopeName):
    descriptionLines = []

    if "description" in function:
        descriptionLines += function["description"].splitlines()

    if "deprecated" in function:
        deprecation = colRed + "Deprecated" + ": " + colGreen + function["deprecated"]
        descriptionLines += deprecation.splitlines()

    for arg in function["args"]:
        if not "description" in arg:
            continue

        argDescription = "{name}{colGreen} - {description}".format(
            name = formatArgumentName(arg["name"]),
            colGreen = colGreen,
            description = arg["description"],
        )

        descriptionLines += argDescription.splitlines()

    return "{availability}{scopePrefix}{name}{signature}{description}".format(
        availability = formatAvailability(function["available"]),
        scopePrefix = scopeName + ":" if scopeName else "",
        name = function["name"],
        signature = formatCallSignature(function),
        description = formatDescription(descriptionLines),
    )

def formatClass(classDefinition):
    result = formatAvailability("both" if "clientName" in classDefinition else "server")

    if "instance" in classDefinition:
        result += classDefinition["instance"] + ": "

    result += classDefinition["name"]

    if "call" in classDefinition:
        result += formatCallSignature(classDefinition["call"])

    if "extend" in classDefinition:
        result += " extends " + classDefinition["extend"]

    if "description" in classDefinition:
        result += formatDescription(classDefinition["description"].splitlines())

    return result

def formatField(field):
    result = formatArgumentName(field["name"])

    types = list(field["types"])
    if "nil" in types:
        types.remove("nil")
        result += "?"

    result += ": " + formatTypes(types)

    if "description" in field:
        result += " {colGreen}-- {line}{colEnd}".format(
            colGreen = colGreen,
            line = field["description"].replace("\n", " "),
            colEnd = colEnd,
        )

    return  result

def formatInterface(interface):
    fields = ["    " + formatField(field) for field in interface["members"]]

    return "{name}:\n{fields}".format(
        name = interface["name"],
        fields = "\n".join(fields),
    )

class ModDotaAPI:
    def __init__(self):
        self.requests_session = requests.Session()
        self.requests_session.headers = {
            'User-agent': 'ModDota_API/1.X (+http://github.com/SinZ163/ModDotaFAQ)'
        }
        self.ReadDump()
    def fetch_page(self, url, timeout=10):
        return self.requests_session.get(url, timeout=timeout).json()
    def ReadDump(self):
        self.api = self.fetch_page("https://unpkg.com/dota-data/files/vscripts/api.json")

MDAPI_logger = logging.getLogger("MDAPI_Reborn")
modDotaAPI = ModDotaAPI()

#called when the bot has loaded everything and is connected
def __initialize__(self, Startup):
    pass
#the command entry point from '=api" or something
def execute(self, name, params, channel, userdata, rank):
    msg = " ".join(params)
    output = channel

    topLevelElements = []
    def checkTopLevelElement(member):
        if msg.lower() in member["name"].lower():
            MDAPI_logger.info("Found a top-level element, "+member["name"])
            topLevelElements.append(member)

    functions = []
    def checkFunction(function, ScopeName=None):
        if msg.lower() in function["name"].lower():
            MDAPI_logger.info("Found a method, "+function["name"])
            functions.append((function, ScopeName))

    for member in modDotaAPI.api:
        if member["kind"] == "function":
            checkFunction(member)
            continue

        checkTopLevelElement(member)
        if member["kind"] == "class":
            for classMember in member["members"]:
                if classMember["kind"] == "function":
                    checkFunction(classMember, member["name"])

    matchedCount = len(topLevelElements + functions)
    if matchedCount == 0:
        self.sendMessage(channel, "No results found.")
    if matchedCount > 5:
        #pm it
        if name == "DB" or matchedCount > 20:
            self.sendMessage(channel, "Too many elements matched ("+str(matchedCount)+"). Please refine your search.")
            return
        else:
            self.sendMessage(channel, "Too many elements matched ("+str(matchedCount)+"). Replying privately.")
            output = name

    for element in topLevelElements:
        if element["kind"] == "class":
            self.sendMessage(output, formatClass(element))
        elif element["kind"] == "interface":
            self.sendMessage(output, formatInterface(element))

    for (function, scopeName) in functions:
        self.sendMessage(output, formatFunction(function, scopeName))
