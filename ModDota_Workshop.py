import requests
import simplejson
import traceback

ID="workshop"
permission=0
class DotaWorkshop:
    def __init__(self):
        with open("commands/ModDota/steamid.txt", "r") as f:
            self.steamid = f.read()
    def fetch_page(self, url, info):
        try:
            headers = { 'User-Agent' : "ModDota_Workshop/1.X (+http://github.com/SinZ163/ModDotaFAQ)" }
        
            r = requests.post(url, data=info)
            return r.json()
        except:
            traceback.print_exc()
            #most likely a timeout
    def GetWorkshopInfo(self, id):
        data = {
            "key" : self.steamid,
            "itemcount" : 1,
            "publishedfileids[0]" : int(id)
        }
        jsonres = self.fetch_page("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/", data)
        #info = simplejson.loads(jsonres, strict = False)
        return jsonres
        
dotaWorkshop = DotaWorkshop()

def execute(self, name, params, channel, userdata, rank):
    if len(params) > 0:
        if params[0].isdigit():
            workshopInfo = dotaWorkshop.GetWorkshopInfo(params[0])
            print("##WORKSHOP_INFO")
            print(workshopInfo)
            print("##END_WORKSHOP_INFO")
            if "response" not in workshopInfo:
                print("what the fuck")
            if workshopInfo["response"]["resultcount"] > 0:
                try:
                    self.sendMessage(channel, "{bold}{title}{bold} {col}03{views}{col} views, {col}04{favorited}{col} favorites ({col}06{lifetime_favorited}{col} lifetime), {col}04{subscriptions}{col} subscriptions ({col}06{lifetime_subscriptions}{col} lifetime) Preview url: {preview_url}".format(bold=chr(2), col=chr(3), **workshopInfo["response"]["publishedfiledetails"][0]))
                except:
                    traceback.print_exc()
            else:
                self.sendMessage(channel, "Invalid or private mod.")
        else:
            self.sendMessage(channel, "This takes numbers, not strings...")
    else:
        self.sendNotice(name, "MatchID is required.")