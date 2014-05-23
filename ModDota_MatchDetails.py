import urllib2
import simplejson

ID="match"
permission=0
class DotaMatchMaking:
    def __init__(self):
        self.useragent = urllib2.build_opener()
        self.useragent.addheaders = [('User-agent', 'ModDota_Prizepool/1.X (+http://github.com/SinZ163/ModDotaFAQ)')]
        with open("commands/ModDota/steamid.txt", "r") as f:
            self.steamid = f.read()
    def fetch_page(self, url, decompress=True, timeout=10):
        try:
            response = self.useragent.open(url, timeout=timeout)
            data = response.read()
            return data
        except:
            pass
            #most likely a timeout
    def GetMatchInfo(self, id):
        jsonres = self.fetch_page("https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/v001/?match_id={matchid}&key={steam}".format(matchid=id,steam=self.steamid))
        info = simplejson.loads(jsonres, strict = False)
        return info["result"]
        
dotaMatch = DotaMatchMaking()

def execute(self, name, params, channel, userdata, rank):
    if len(params) > 0:
        matchInfo = dotaMatch.GetMatchInfo(params[0])
        if "error" in matchInfo:
            self.sendMessage(channel, "Error: "+matchInfo["error"])
        else:
            #ok, there is valid info here
            msg = []
            #Ok, lets do winner.
            if matchInfo["leagueid"] == 0:
                if matchInfo["radiant_win"]:
                    msg.append("Radiant Victory!")
                else:
                    msg.append("Dire Victory!")
            else:
                if matchInfo["radiant_win"]:
                    msg.append(chr(2)+chr(3)+"03"+matchInfo["radiant_name"]+chr(3)+chr(2)+" vs "+chr(3)+"04"+matchInfo["dire_name"]+chr(3))
                else:
                    msg.append(chr(3)+"03"+matchInfo["radiant_name"]+chr(3)+" vs "+chr(2)+chr(3)+"04"+matchInfo["dire_name"]+chr(3)+chr(2))
            #Ok, lets do duration now
            if matchInfo["duration"] > 60*60:
                #we have hours
                msg.append("Duration: "+str((matchInfo["duration"] // 60)//60)+":"+str((matchInfo["duration"] // 60)%60)+":"+str(matchInfo["duration"] % 60))
            elif matchInfo["duration"] > 60:
                msg.append("Duration: "+str(matchInfo["duration"] // 60)+":"+str(matchInfo["duration"]%60))
                #we have minutes
            else:
                #dafuq, only seconds
                msg.append("Duration: "+str(matchInfo["dutation"])+" Seconds!!")
            #Ok, lets do score now
            radScore = 0
            dirScore = 0
            for player in matchInfo["players"]:
                if player["player_slot"] < 5:
                    radScore = radScore + player["kills"]
                else:
                    dirScore = dirScore + player["kills"]
            msg.append("Score: {col}03{rad}{col}{bold}:{bold}{col}04{dir}{col}".format(rad=radScore,dir=dirScore, col=chr(3), bold=chr(2)))
            #people are scrubs to type this in their browser themselves >.>
            msg.append("Dotabuff: http://dotabuff.com/matches/"+params[0])
            #We are done!
            self.sendMessage(channel, (chr(2)+" | "+chr(2)).join(msg))
    else:
        self.sendNotice(name, "MatchID is required.")