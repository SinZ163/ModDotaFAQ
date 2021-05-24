import requests
import simplejson

import time
import traceback

ID="prize"
permission=0

class ModDotaPrizePool:
    prizeList = {
    }
    def __init__(self):
        self.requests_session = requests.Session()
        self.requests_session.headers = {
            'User-agent': 'ModDota_Prizepool/1.X (+http://github.com/SinZ163/ModDotaFAQ)'
        }
        with open("commands/ModDota/steamid.txt", "r") as f:
            self.steamid = f.read()
    def loadDB(self, url=None):
        if url == None:
            modList = open("commands/ModDota/prizepool.json", "r")
            fileInfo = modList.read()
        else:
            fileInfo = self.fetch_page(url)
        self.info = simplejson.loads(fileInfo, strict = False)
    def SaveDB(self):
        with open("commands/ModDota/prizepool.json", "w") as f:
            f.write(simplejson.dumps(self.info, sort_keys=True, indent=4 * ' ').encode("utf-8"))
    def fetch_page(self, url, timeout=10, decode_json=False):
        request = self.requests_session.get(url, timeout=timeout)
        if decode_json:
            return request.json()
        else:
            return request.text
    def CheckLeague(self, id):
        info = self.fetch_page("http://api.steampowered.com/IEconDOTA2_570/GetTournamentPrizePool/v1?key={key}&leagueid={league}".format(key=self.steamid, league=id))
        print(info)
        if info:
            return simplejson.loads(info)["result"]["prize_pool"]
        else:  
            return -1

    ##def SendMessage(self, channel, msg):
    ##    print("Doing workaround SendMessage!")
    ##    print("Channel: "+channel)
    ##    print("Message: "+msg)
    ##    self.cmdhdlr.SendMessage(channel, msg)
        
modDotaPrizePool = ModDotaPrizePool()

def __initialize__(self, Startup):
    if "MDPP" in self.threading.pool:  
        self.threading.sigquitThread("MDPP")
    #initiate the db
    modDotaPrizePool.loadDB()
    
    #initiate automated tracking
    for league in modDotaPrizePool.info["leagues"]:
        if league["id"] in modDotaPrizePool.prizeList:
            continue
        else:
            modDotaPrizePool.prizeList[league["id"]] = 0
    
def PrizePoolThread(self, pipe):
    cmdhdlr = self.base
    
    while self.signal == False:
        try:
            print("Still alive..")
            #print(modDotaPrizePool.info)
            for league in modDotaPrizePool.info["leagues"]:
                prizeCount = modDotaPrizePool.CheckLeague(int(league["id"]))
                print(modDotaPrizePool.prizeList[league["id"]])
                if prizeCount > modDotaPrizePool.prizeList[league["id"]]:
                    #ok, it grew since last time
                    hasStretchGoal = False
                    
                    for stretchGoal in league["stretchGoals"]:
                        #print "stretchgoal:", stretchGoal
                        if "completed" in stretchGoal:
                            #print "stretchgoal completed?"
                            continue
                        else:
                            #print "stretchgoal not completed. prizeCount: {0}, stretchGoal: {1}".format(prizeCount,
                            #                                                                            stretchGoal["prize"])
                            #print prizeCount > stretchGoal["prize"]
                            #print type(prizeCount), type(stretchGoal["prize"])
                            if prizeCount > int(stretchGoal["prize"]):
                                #print "Announce new Stretchgoal"
                                #OK, we have a new stretchgoal to announce
                                cmdhdlr.sendMessage("#dota2mods,#sinzationaldota", "New stretch goal hit!")
                                #cmdhdlr.sendMessage("#test", "Stretch Goal "+league["stretchGoals"].index(stretchGoal)+", "+stretchGoal["name"]+" ("+stretchGoal["prize"]+")")
                                #print league["stretchGoals"].index(stretchGoal), stretchGoal["name"]
                                try:
                                    cmdhdlr.sendMessage("#dota2mods,#sinzationaldota", "Stretch Goal {0}, {1} (${2:,}) {3}".format(league["stretchGoals"].index(stretchGoal)+1,
                                                                                                      stretchGoal["name"].encode("utf-8"),
                                                                                                      int(stretchGoal["prize"]),
                                                                                                      stretchGoal["description"].encode("utf-8")
                                                                                                      ))
                                    stretchGoal["completed"] = True
                                    league["milestone"] = (prizeCount // 100000)
                                    modDotaPrizePool.SaveDB()
                                except Exception as error:
                                    traceback.print_exc()
                                hasStretchGoal = True
                                
                    if hasStretchGoal == False:
                        #Did we actually have a milestone?
                        if "milestone" in league:        
                            #Did we pass a milestone?
                            if (prizeCount // 100000) > league["milestone"]:
                                #We hit a milestone, lets announce this!
                                cmdhdlr.sendMessage("#dota2mods,#sinzationaldota", "TI7's Prize pool just reached the ${0:,d} milestone, currently at ${1:,d}".format((prizeCount // 100000)*100000, prizeCount))
                                league["milestone"] = (prizeCount // 100000)
                                
                                modDotaPrizePool.SaveDB()
                        else:
                            league["milestone"] = (prizeCount // 100000)
                            modDotaPrizePool.SaveDB()
                            
            #We need to sleep for 5 minutes or so, but doing a big 5 minute sleep will be a big delay if somthing were to happen
            #but 15 seconds is nothing, so we should sleep 20 times
            sleepCount = 0
            while (sleepCount <= 20):
                if self.signal:
                    print("While sleeping, we were told to gtfo, gtfoing!")
                    break
                sleepCount = sleepCount + 1
                time.sleep(15)
        except:
            traceback.print_exc()
    print("RIP MDPP, 2014 - 2014")
    
def execute(self, name, params, channel, userdata, rank):
    if len(params) == 0:
        #Ok, default is ti4, because yolo
        self.sendMessage(channel, "TI7 Prize Pool: ${0:,}".format(modDotaPrizePool.CheckLeague(5401)))
    elif len(params) == 1:
        #ok, We have one argument, meaning its a leagueID
        self.sendMessage(channel, str(params[0])+" Prize pool: ${0:,}".format(modDotaPrizePool.CheckLeague(params[0])))
    else:
        #ok, we need to handle this like a real command now
        if params[0] == "running":
            if params[1] == "true":
                #Ok, start the engine
                if not "MDPP" in self.threading.pool:
                    self.threading.addThread("MDPP", PrizePoolThread, self)
                else:
                    self.sendMessage(channel, "Already running")
        if params[0] == "load":
            modDotaPrizePool.loadDB(params[1])
            
