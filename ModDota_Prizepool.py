import urllib2
import simplejson

import StringIO
import gzip

import time
import traceback

ID="prize"
permission=0

class ModDotaPrizePool:
    prizeList = {
    }
    def __init__(self):
        self.useragent = urllib2.build_opener()
        self.useragent.addheaders = [
            ('User-agent', 'ModDota_Prizepool/1.X (+http://github.com/SinZ163/ModDotaFAQ)'),
            ('Accept-encoding', 'gzip')
        ]
    def loadDB(self):
        
        modList = open("commands/ModDota/prizepool.json", "r")
        fileInfo = modList.read()
        self.info = simplejson.loads(fileInfo, strict = False)
    def SaveDB(self):
        with open("commands/ModDota/prizepool.json", "w") as f:
            f.write(simplejson.dumps(self.info, sort_keys=True, indent=4 * ' ').encode("utf-8"))
    def fetch_page(self, url, decompress=True, timeout=10):
        try:
            response = self.useragent.open(url, timeout=timeout)
            if response.info().get('Content-Encoding') == 'gzip' and decompress:
                print "DOING DECOMPRESSION"
                buf = StringIO(response.read())
                f = gzip.GzipFile(fileobj=buf, mode='rb')
                data = f.read()
            else:
                data = response.read()
            return data
        except:
            pass
            #most likely a timeout
    def CheckLeague(self, id):
        info = self.fetch_page("http://api.steampowered.com/IEconDOTA2_570/GetTournamentPrizePool/v1?key={key}&leagueid={league}".format(key=self.info["id"], league=id))
        print(info)
        return simplejson.loads(info)["result"]["prize_pool"]

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
        print("Still alive..")
        
        for league in modDotaPrizePool.info["leagues"]:
            prizeCount = modDotaPrizePool.CheckLeague(league["id"])
            
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
                            cmdhdlr.sendMessage("#dota2mods", "New stretch goal hit!")
                            #cmdhdlr.sendMessage("#test", "Stretch Goal "+league["stretchGoals"].index(stretchGoal)+", "+stretchGoal["name"]+" ("+stretchGoal["prize"]+")")
                            #print league["stretchGoals"].index(stretchGoal), stretchGoal["name"]
                            try:
                                cmdhdlr.sendMessage("#dota2mods", "Stretch Goal {0}, {1} ({2})".format(league["stretchGoals"].index(stretchGoal)+1,
                                                                                                  stretchGoal["name"].encode("utf-8"),
                                                                                                  stretchGoal["prize"].encode("utf-8")
                                                                                                  ))
                                stretchGoal["completed"] = True
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
                            cmdhdlr.sendMessage("#dota2mods", "TI4's Prize pool just reached the "+str((prizeCount // 100000)*100000)+ " milestone, currently at "+str(prizeCount))
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
    print("RIP MDPP, 2014 - 2014")
    
def execute(self, name, params, channel, userdata, rank):
    if len(params) == 0:
        #Ok, default is ti4, because yolo
        self.sendMessage(channel, "TI4 Prize Pool: "+str(modDotaPrizePool.CheckLeague(600)))
    elif len(params) == 1:
        #ok, We have one argument, meaning its a leagueID
        self.sendMessage(channel, str(params[0])+" Prize pool: "+str(modDotaPrizePool.CheckLeague(params[0])))
    else:
        #ok, we need to handle this like a real command now
        if params[0] == "running":
            if params[1] == "true":
                #Ok, start the engine
                if not "MDPP" in self.threading.pool:
                    self.threading.addThread("MDPP", PrizePoolThread, self)
                else:
                    self.sendMessage(channel, "Already running")