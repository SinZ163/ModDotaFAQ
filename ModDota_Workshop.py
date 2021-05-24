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

            r = requests.get(url, params=info)
            print(r.text)
            return r.json()
        except:
            traceback.print_exc()
            #most likely a timeout
    def GetWorkshopInfo(self, id):
        data = {
            "key" : self.steamid,
            "includetags" : 1,
            "publishedfileids[0]" : int(id)
        }
        jsonres = self.fetch_page("https://api.steampowered.com/IPublishedFileService/GetDetails/v1/", data)
        #info = simplejson.loads(jsonres, strict = False)
        return jsonres

dotaWorkshop = DotaWorkshop()

def execute(self, name, params, channel, userdata, rank):
    if len(params) > 0:
        if params[0].isdigit():
            try:
                workshopInfo = dotaWorkshop.GetWorkshopInfo(params[0])
                print("##WORKSHOP_INFO")
                print(workshopInfo)
                print("##END_WORKSHOP_INFO")
                if "response" not in workshopInfo:
                    print("what the fuck")
                if workshopInfo["response"]["publishedfiledetails"][0]["result"] == 1:
                    try:
                        dedi = ""
                        if "tags" in workshopInfo["response"]["publishedfiledetails"][0]:
                            for tag in workshopInfo["response"]["publishedfiledetails"][0]["tags"]:
                                if tag["tag"] == "CGDedicatedServerEnabled":
                                    dedi = "{col}03{bold}{msg}{bold}{col} ".format(bold=chr(2),col=chr(3),msg="Dedicated Enabled")
                        self.sendMessage(channel, u"{bold}{title}{bold} {col}03{views}{col} views, {col}04{favorited}{col} favorites ({col}06{lifetime_favorited}{col} lifetime), {col}04{subscriptions}{col} subscriptions ({col}06{lifetime_subscriptions}{col} lifetime) {dedi}URL: http://steamcommunity.com/sharedfiles/filedetails/?id={publishedfileid}".format(bold=chr(2), col=chr(3), dedi=dedi, **workshopInfo["response"]["publishedfiledetails"][0]))
                    except:
                        traceback.print_exc()
                else:
                    self.sendMessage(channel, "Invalid or private mod.")
            except:
                self.sendMessage(channel, "oops")
                traceback.print_exc()
        else:
            self.sendMessage(channel, "This takes numbers, not strings...")
    else:
        self.sendNotice(name, "worrkshop ID is required.")