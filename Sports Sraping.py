import bs4
import time
import os
import json
from bs4 import BeautifulSoup as soup
import requests, pandas as pd


StartSeason = 2018
EndSeason = 2024

class General:
        def __init__(self,dict):
            self.games = dict["games"]
            self.games_started = dict["games_started"]

class Rushing:
        def __init__(self,dict):
            self.rush_att = dict["rush_att"]
            self.rush_yds = dict["rush_yds"]
            self.rush_td = dict["rush_td"]
            self.rush_first_down = dict["rush_first_down"]
            self.rush_long = dict["rush_long"]
            self.rush_yds_per_att = dict["rush_yds_per_att"]
            self.rush_yds_per_g = dict["rush_yds_per_g"]
            self.rush_att_per_g = dict["rush_att_per_g"]
            self.fumbles = dict["fumbles"]
class Receiving:
        def __init__(self,dict):
            self.targets = dict["targets"]
            self.rec = dict["rec"]
            self.rec_yds = dict["rec_yds"]
            self.rec_yds_per_rec = dict["rec_yds_per_rec"]
            self.rec_td = dict["rec_td"]
            self.rec_first_down = dict["rec_first_down"]
            self.rec_long = dict["rec_long"]
            self.rec_per_g = dict["rec_per_g"]
            self.rec_yds_per_g = dict["rec_yds_per_g"]
            self.catch_pct = dict["catch_pct"]
            self.rec_yds_per_tgt = dict["rec_yds_per_tgt"]

class Passing:
        def __init__(self,dict):
            self.pass_cmp = dict["pass_cmp"]
            self.pass_att = dict["pass_att"]
            self.pass_cmp_pct = dict["pass_cmp_pct"]
            self.pass_yds = dict["pass_yds"]
            self.pass_td = dict["pass_td"]
            self.pass_td_pct = dict["pass_td_pct"]
            self.pass_int = dict["pass_int"]
            self.pass_int_pct = dict["pass_int_pct"]
            self.pass_first_down = dict["pass_first_down"]
            self.pass_long = dict["pass_long"]
            self.pass_yds_per_att = dict["pass_yds_per_att"]
            self.pass_adj_yds_per_att = dict["pass_adj_yds_per_att"]
            self.pass_yds_per_cmp = dict["pass_yds_per_cmp"]
            self.pass_yds_per_g = dict["pass_yds_per_g"]
            self.pass_rating = dict["pass_rating"]
            self.pass_sacked = dict["pass_sacked"]
            self.pass_sacked_yds = dict["pass_sacked_yds"]
            self.pass_sacked_pct = dict["pass_sacked_pct"]
            self.pass_net_yds_per_att = dict["pass_net_yds_per_att"]
            self.pass_adj_net_yds_per_att = dict["pass_adj_net_yds_per_att"]


class Season:
    def __init__(self, year):
        self.year = year
        self.General = None
        self.Passing = None
        self.Rushing = None
        self.Receiving = None
    


class Player:
    def __init__(self, name, id, pos ,stats):
        self.name = name
        self.id = id
        self.pos = pos
        self.stats = stats
        self.totals = dict()

    def getTotals(self):
        totalDict = dict()
        finDict = dict()
        for key in self.stats:
            genStats = vars(self.stats[key].General)
            passStats = vars(self.stats[key].Passing)
            rushStats = vars(self.stats[key].Rushing)
            recStats = vars(self.stats[key].Receiving)
            for item in genStats:
                totalDict.setdefault(item,[]).append(genStats[item][0]) 
            for item in passStats:
                totalDict.setdefault(item,[]).append(passStats[item][0])
            for item in rushStats:
                totalDict.setdefault(item,[]).append(rushStats[item][0])
            for item in recStats:
                totalDict.setdefault(item,[]).append(recStats[item][0])
        for dictKey in totalDict:         
            cal = statCalculations(totalDict,dictKey)
            finDict.setdefault(StatsRef[dictKey],[]).append(cal)
        return finDict

    # def getData(self):
        


passArr = []
statsIgnore = ["pos","qbr","awards","ranker","team_name_abbr","age","pass_success","name_display","reason"]
StatsRef = {"Player":"General☳Player","pos":"General☳Pos","games":"General☳G","games_started":"General☳GS","qb_rec":"General☳Record","pass_cmp":"Passing☳Cmp","pass_att":"Passing☳Att","pass_cmp_pct":"Passing☳Cmp%","pass_yds":"Passing☳Yds","pass_td":"Passing☳TD","pass_td_pct":"Passing☳TD%","pass_int":"Passing☳Int","pass_int_pct":"Passing☳Int%","pass_first_down":"Passing☳1D","pass_long":"Passing☳Long","pass_yds_per_att":"Passing☳Y/A","pass_adj_yds_per_att":"Passing☳AY/A","pass_yds_per_cmp":"Passing☳Y/Cmp","pass_yds_per_g":"Passing☳Y/G","pass_rating":"Passing☳Rating","pass_sacked":"Passing☳Sk","pass_sacked_yds":"Passing☳Sk Yds","pass_sacked_pct":"Passing☳Sk%","pass_net_yds_per_att":"Passing☳NY/A","pass_adj_net_yds_per_att":"Passing☳ANY/A","rush_att":"Rushing☳Att","rush_yds":"Rushing☳Yds","rush_td":"Rushing☳TD","rush_first_down":"Rushing☳1D","rush_long":"Rushing☳Long","rush_yds_per_att":"Rushing☳Y/A","rush_yds_per_g":"Rushing☳Y/G","rush_att_per_g":"Rushing☳Att/G","targets":"Receiving☳Tgt","rec":"Receiving☳Rec","rec_yds":"Receiving☳Yds","rec_yds_per_rec":"Receiving☳Y/R","rec_td":"Receiving☳TD","rec_first_down":"Receiving☳1D","rec_long":"Receiving☳Long","rec_per_g":"Receiving☳R/G","rec_yds_per_g":"Receiving☳Y/G","catch_pct":"Receiving☳Ctch%","rec_yds_per_tgt":"Receiving☳Y/T","fumbles":"Misc☳Fmb","comebacks":"Misc☳4QC","gwd":"Misc☳GWD"}
playerObj = dict()
playerObjArr = []
playersArr = dict()
data = dict()
dataframes = dict()


StatType = [{"stat":"passing","sort":"pass_att"},{"stat":"rushing","sort":"rush_att"},{"stat":"receiving","sort":"targets"}]
Qualifier = 5


def find(arr, id):
    for x in arr:
        if x.id == id:
            return x
def findYear(arr, year):
    for x in arr:
        if x.year == year:
            return x

def GetPlayer(row):
        for cell in row.findAll('td'):
            if cell.attrs["data-stat"] == "name_display":
                playerID = cell.attrs["data-append-csv"]
                playerName = cell.text
            elif cell.attrs["data-stat"] == "pos":
                position = cell.text
            else:
                continue
        if playerID in playersArr:
            player = playersArr[playerID]
            # print("{0} already exists in Players Array".format(playerName))
            return player
        else:
            player = Player(playerName,playerID,position,dict())
            playersArr.setdefault(playerID,player)
            return player
            

def LeaderStats():
    x = range(StartSeason,EndSeason + 1)
    for Season in x:
        for stat in StatType:
            time.sleep(5)
            SeasonUrl = "https://www.pro-football-reference.com/years/{0}/{1}.htm#{1}::{2}".format(Season,stat["stat"],stat["sort"])
            print(SeasonUrl)
            page = soup(requests.get(SeasonUrl).text, 'html.parser')
            table = page.find('table', id=StatType)
            for row in table.tbody.find_all('tr'):
                fetchedPlayer = GetPlayer(row)
                # print(fetchedPlayer)
                if any(player["ID"] == fetchedPlayer["ID"] for player in playersArr): ## If player already in list
                    checkPlayer = find(playersArr, fetchedPlayer["ID"])
                    fetchedPlayer = checkPlayer
                    stats = fetchedPlayer["Seasons"]
                    newStat = GetTableRow(row,stats)
                    # for idx, item in enumerate(playersArr):
                    #     if (player["ID"] == fetchedPlayer["ID"] for player in item):
                    #         print(idx)
                
                else:
                    stats = dict()
                    GetHeaders(table,stats)
                    fetchedPlayer.setdefault("Seasons",stats)
                    GetTableRow(row,stats)
                    playersArr.append(fetchedPlayer)
                
                print(fetchedPlayer)

                # fetchedPlayer.stat
                # GetHeaders(table)
                # data.setdefault("year",str(Season))
                # # GetTableRow()
                # for cell in row.findAll('td'):
                #     if cell.attrs["data-stat"] == "name_display":
                #         playerID = cell.attrs["data-append-csv"]
                #         playerName = cell.text
                #         # playerObj.setdefault("name",playerName)
                #         # playerObj.setdefault("id",playerID)
                #     else:
                #         attr = cell.attrs["data-stat"]
                #         data.setdefault(attr,[]).append(cell.text)
                # for key in data:
                #     if len(data[key]) < 1 :
                #          data[key].append("")
                #     # print("General",len(data["General☳Year"]), key,len(data[key]))
                #     # if len(data["ranker"]) != len(data[key]):
                #     #     data[key].append("")
                # df = pd.DataFrame(data)
                # statsArr = [df]
                # player = Player(playerName,playerID,statsArr)
                # if player.id in [player.id for player in playersArr]:
                #     player.stats.append(df)
                #     data.clear()
                # else:
                #     playersArr.append(player)
                #     data.clear()
def _sum(arr):
    # initialize a variable
    # to store the sum
    # while iterating through
    # the array later
    sum = 0
 
    # iterate through the array
    # and add each element to the sum variable
    # one at a time
    for i in arr:
        sum = sum + int(i)
 
    return(sum)
def statCalculations(dictionary,stat):
    games = _sum(dictionary["games"])
    pass_att = _sum(dictionary["pass_att"])
    pass_cmp = _sum(dictionary["pass_cmp"])
    pass_yds = _sum(dictionary["pass_yds"])
    pass_td = _sum(dictionary["pass_td"])
    pass_int = _sum(dictionary["pass_int"])
    pass_first_down = _sum(dictionary["pass_first_down"])
    pass_sacked = _sum(dictionary["pass_sacked"])
    pass_sacked_yds = _sum(dictionary["pass_sacked_yds"])
    rush_att = _sum(dictionary["rush_att"])
    rush_yds = _sum(dictionary["rush_yds"])
    rush_td = _sum(dictionary["rush_td"])
    rush_first_down = _sum(dictionary["rush_first_down"])
    targets = _sum(dictionary["targets"])
    rec = _sum(dictionary["rec"])
    rec_yds = _sum(dictionary["rec_yds"])
    rec_td = _sum(dictionary["rec_td"])
    rec_first_down = _sum(dictionary["rec_first_down"])



    if stat == "pos":
        return dictionary[stat][0]
    if stat == "games" or stat == "games_started" or stat == "pass_cmp" or stat == "pass_att" or stat == "pass_yds" or stat == "pass_td" or stat == "pass_int" or stat == "pass_first_down" or stat == "pass_sacked" or stat == "pass_sacked_yds" or stat == "comebacks" or stat == "gwd" or stat == "rush_att" or stat == "rush_yds" or stat == "rush_td" or stat == "rush_first_down" or stat == "targets" or stat == "rec" or stat == "rec_yds" or stat == "rec_td" or stat == "rec_first_down" or stat == "fumbles":
        return _sum(dictionary[stat])
    if stat == "qb_rec":
        w = 0
        l = 0
        t = 0
        for item in dictionary[stat]:
            if item != "":
               splitlist = item.split("-")
               w = w + int(splitlist[0])
               l = l + int(splitlist[1])
               t = t + int(splitlist[2])
        return "{0}-{1}-{2}".format(w,l,t)
    if stat == "pass_cmp_pct": 
        if pass_att == 0:
            return 0  
        else:     
            return round(pass_cmp/pass_att,4)
    if stat == "pass_td_pct":
        if pass_att == 0:
            return 0  
        else:    
            return round(pass_td/pass_att,4)
    if stat == "pass_int_pct":
        if pass_att == 0:
            return 0  
        else:    
            return round(pass_int/pass_att,4)
    if stat == "pass_long":    
        return max(dictionary["pass_long"])
    if stat == "rush_long":    
        return max(dictionary["rush_long"])
    if stat == "rec_long":    
        return max(dictionary["rec_long"])
    if stat == "pass_yds_per_att":
        if pass_att == 0:
            return 0  
        else:    
            return round(pass_yds/pass_att,2)
    if stat == "pass_adj_yds_per_att":
        if pass_att == 0:
            return 0  
        else:   
            return round((pass_yds + 20 * pass_td - 45 * pass_int)/(pass_att),2)
    if stat == "pass_yds_per_cmp": 
        if pass_cmp == 0:
            return 0  
        else:  
            return round((pass_yds/pass_cmp),2)
    if stat == "pass_yds_per_g":    
        return round((pass_yds/games),2)
    if stat == "pass_rating":
        return round(CalcQBRate(pass_cmp,pass_att,pass_yds,pass_td,pass_int),2)
    if stat == "pass_sacked_pct":
        if pass_att + pass_sacked == 0:
            return 0  
        else:
            return round((pass_sacked/(pass_att + pass_sacked)),4)
    if stat ==  "pass_net_yds_per_att":
        if pass_att + pass_sacked == 0:
            return 0  
        else:
            return round((pass_yds - pass_sacked_yds)/(pass_att + pass_sacked),2)
    if stat ==  "pass_adj_net_yds_per_att":
        if pass_att + pass_sacked == 0:
            return 0  
        else:
            return round((pass_yds - pass_sacked_yds + (20 * pass_td) - (45 * pass_int))/(pass_att + pass_sacked),2)
    if stat == "rush_yds_per_att":
        if rush_att == 0:
            return 0
        else:
            return round(rush_yds/rush_att,2)
    if stat == "rush_yds_per_g":
        return round(rush_yds/games,2)
    if stat == "rush_att_per_g":
        return round(rush_att/games,1)
    if stat == "rec_yds_per_rec":
        if rec == 0:
            return 0
        else:
            return round(rec_yds/rec,1)
    if stat == "rec_per_g":
        return round(rec/games,1)
    if stat == "rec_yds_per_g":
        return round(rec_yds/games,1)
    if stat == "rec_yds_per_tgt":
        if targets == 0:
            return 0
        else:
            return round(rec_yds/targets,2)
    if stat == "catch_pct":
        if targets == 0:
            return 0
        else:
            return round(rec/targets,4)
def CalcQBRate(cmp,att,yds,td,int):
    if att == 0:
        return 0
    else:
        a = (cmp/att - 0.3) * 5
        b = (yds/att - 3) * 0.25
        c = (td/att) * 20
        d = 2.375 - (int/att * 25)
        rate = ((a + b + c + d)/6) * 100
        return rate
def GetHeaders(table,dictionary):
    for row in table.thead.find_all('tr'):
        if "class" in  row.attrs:
            # print(row)
            if row.attrs["class"] == "over_header":
                continue
        else:
            for column in row.find_all('th'):
                attr = column.attrs["data-stat"]
                if attr in statsIgnore:
                    continue
                dictionary.setdefault(attr,[])
def GetTableRow(row,dictionary):
        # first_column = row.findAll('th')[0]
        # dictionary.setdefault(first_column.attrs["data-stat"],[]).append(first_column.text)
        for cell in row.findAll('td'):
            attr = cell.attrs["data-stat"]
            if attr in statsIgnore:
                continue
            if attr not in dictionary:
                continue
            dictionary.setdefault(attr,[]).append(cell.text)
            # if len(dictionary[attr]) < max:
                
        # for key in dictionary:
        #     if len(dictionary[key]) < 1 :
        #         dictionary[key].append("")
        return dictionary
def FillStats(player,Season):
 print("du")



def SeasonStats(Season):
    # time.sleep(11)
    passTable = GetPassing(Season)
    rushTable = GetRushing(Season)
    # recTable = GetReceiving(Season)

    for player in playersArr:
        if str(Season) in playersArr[player].stats:           
            if playersArr[player].stats[str(Season)].Passing == None:
                passDict = dict()
                GetHeaders(passTable,passDict)
                for keys in passDict:
                    passDict[keys].append("0")
                passing = Passing(passDict)
                playersArr[player].stats[str(Season)].Passing = passing
            if playersArr[player].stats[str(Season)].Rushing == None:
                rushDict = dict()
                GetHeaders(rushTable,rushDict)
                for keys in rushDict:
                    rushDict[keys].append("0") 
                rushing = Rushing(rushDict)
                playersArr[player].stats[str(Season)].Rushing = rushing
            if playersArr[player].stats[str(Season)].Receiving == None:
                recDict = dict()
                GetHeaders(rushTable,recDict)
                for keys in recDict:
                    recDict[keys].append("0") 
                receiving = Receiving(recDict)
                playersArr[player].stats[str(Season)].Receiving = receiving



def save_xls(list_dfs, xls_path):
    with pd.ExcelWriter(xls_path) as writer:
        for  name, frame  in list_dfs.items():
             frame.to_excel(writer, sheet_name = name)


def GetPassing(year):
    print(" --{0} Passing".format(year))
    # time.sleep(5)
    PassingUrl = "https://www.pro-football-reference.com/years/{0}/passing.htm#passing::pass_att".format(year)
    passing = soup(requests.get(PassingUrl).text, 'html.parser')
    table = passing.find('table', id="passing")
    for row in table.tbody.find_all('tr'):
                dictionary = dict()
                GetHeaders(table,dictionary)
                fetchedPlayer = GetPlayer(row)
                newStat = GetTableRow(row,dictionary)
                if str(year) in fetchedPlayer.stats:
                    fetchedSeason = fetchedPlayer.stats[str(year)]
                    fetchedSeason.Passing = Passing(newStat)
                    if fetchedSeason.General == None:
                        fetchedSeason.General = General(newStat)
                else:
                    fetchedSeason = Season(year)
                    fetchedSeason.General = General(newStat)
                    fetchedSeason.Passing = Passing(newStat)
                    player = playersArr[fetchedPlayer.id]
                    player.stats.setdefault(str(year),fetchedSeason)
    return table
def GetRushing(year):
    print(" --{0} Rushing".format(year))
    # time.sleep(5)
    RushingUrl = "https://www.pro-football-reference.com/years/{0}/scrimmage.htm#scrimmage::rush_att".format(year)
    rushing = soup(requests.get(RushingUrl).text, 'html.parser')
    table = rushing.find('table', id="scrimmage")
    for row in table.tbody.find_all('tr'):
                dictionary = dict()
                GetHeaders(table,dictionary)
                fetchedPlayer = GetPlayer(row)
                newStat = GetTableRow(row,dictionary)
                if str(year) in fetchedPlayer.stats:
                    fetchedSeason = fetchedPlayer.stats[str(year)]
                    fetchedSeason.Rushing = Rushing(newStat)
                    fetchedSeason.Receiving = Receiving(newStat)
                    if fetchedSeason.General == None:
                        fetchedSeason.General = General(newStat)
                else:
                    fetchedSeason = Season(year)
                    fetchedSeason.Rushing = Rushing(newStat)
                    fetchedSeason.Receiving = Receiving(newStat)
                    fetchedSeason.General = General(newStat)
                    player = playersArr[fetchedPlayer.id]
                    player.stats.setdefault(str(year),fetchedSeason)
    return table                
def GetReceiving(year):
    print(" --{0} Receiving".format(year))
    # time.sleep(5)
    ReceivingUrl = "https://www.pro-football-reference.com/years/{0}/receiving.htm#receiving::targets".format(year)
    receiving = soup(requests.get(ReceivingUrl).text, 'html.parser')
    table = receiving.find('table', id="receiving")
    for row in table.tbody.find_all('tr'):
                dictionary = dict()
                GetHeaders(table,dictionary)
                fetchedPlayer = GetPlayer(row)
                newStat = GetTableRow(row,dictionary)
                if str(year) in fetchedPlayer.stats:
                    fetchedSeason = fetchedPlayer.stats[str(year)]
                    fetchedSeason.Receiving = Receiving(newStat)
                    if fetchedSeason.General == None:
                        fetchedSeason.General = General(newStat)
                else:
                    fetchedSeason = Season(year)
                    fetchedSeason.Receiving = Receiving(newStat)
                    fetchedSeason.General = General(newStat)
                    player = playersArr[fetchedPlayer.id]
                    player.stats.setdefault(str(year),fetchedSeason)
    return table





def Run():
    LeaderStats()
    playerDict = dict()
    for player in playersArr:    
        playerDict.setdefault("Player",[]).append(player["Name"])
        for key in player["Seasons"]:
            if key == "qbr" or key == "awards" or key == "ranker" or key == "team_name_abbr" or key == "age" or key == "pass_success" or key == "name_display" :
                continue
            else:
                cal = statCalculations(player["Seasons"],key) 
                playerDict.setdefault(StatsRef[key],[]).append(cal)
        print(playerDict)
    df = pd.DataFrame(playerDict)
    df.columns = pd.MultiIndex.from_tuples([tuple(c.split("☳")) for c in df.columns])
    with pd.ExcelWriter('Output\{0} to {1}.xlsx'.format(StartSeason,EndSeason)) as writer:
        df.to_excel(writer, sheet_name = '{0} to {1}'.format(StartSeason,EndSeason))
        workbook = writer.book
        worksheet = writer.sheets['{0} to {1}'.format(StartSeason,EndSeason)]
        percent = workbook.add_format({"num_format": "0%"})
        worksheet.set_column(7, 7, None, percent)
        worksheet.set_column(10, 10, None, percent)
        worksheet.set_column(12, 12, None, percent)
        worksheet.set_column(22, 22, None, percent)
        worksheet.set_column(43, 43, None, percent)
    # df.to_csv('{0} to {1}.csv'.format(StartSeason,EndSeason), index=False) 
    print(df)








def Test():
    x = range(StartSeason,EndSeason + 1)
    finalDict = dict()
    for Season in x:
        print("Starting Season {0}".format(Season))
        SeasonStats(Season)
        # if Season != EndSeason:
            # time.sleep(8)
    for player in playersArr:
        print("Getting Totals for {0}".format(playersArr[player].name))
        playersArr[player].totals = playersArr[player].getTotals()
        finalDict.setdefault(StatsRef["Player"],[]).append( playersArr[player].name)
        finalDict.setdefault(StatsRef["pos"],[]).append( playersArr[player].pos)
        for stats in playersArr[player].totals:
             finalDict.setdefault(stats,[]).append(playersArr[player].totals[stats][0])
    df = pd.DataFrame(finalDict)
    df.columns = pd.MultiIndex.from_tuples([tuple(c.split("☳")) for c in df.columns])
    with pd.ExcelWriter('Output\{0} to {1}.xlsx'.format(StartSeason,EndSeason)) as writer:
        df.to_excel(writer, sheet_name = '{0} to {1}'.format(StartSeason,EndSeason))
        workbook = writer.book
        worksheet = writer.sheets['{0} to {1}'.format(StartSeason,EndSeason)]
        percent = workbook.add_format({"num_format": "0%"})
        worksheet.set_column(7, 7, None, percent)
        worksheet.set_column(10, 10, None, percent)
        worksheet.set_column(12, 12, None, percent)
        worksheet.set_column(22, 22, None, percent)
        worksheet.set_column(43, 43, None, percent)
    print("done")


Test()


# Mark -  Player Retrieval Testing 



# url = 'https://www.pro-football-reference.com/years/2024/rushing.htm'
# print(url)
# splits = soup(requests.get(url).text, 'html.parser')
# table = splits.find('table', id="rushing")
# GetHeaders(table,data)
# # print(data)


# # Testing With Jalen Hurts
# url = 'https://www.pro-football-reference.com/players/T/TomlLa00/gamelog/'
# print(url)
# splits = soup(requests.get(url).text, 'html.parser')
# table = splits.find('table', id="stats")
# GetHeaders(table)
# for row in table.tbody.findAll('tr'):
#     GetTableRow(row)
# lens = map(len, data.values())
# if len(set(lens)) == 1:
#     df = pd.DataFrame(data)
#     print(df)
# else:
#     print("Error")    


# for row in table.thead.find_all('tr'):
#     # print(row.attrs)
#     if "class" in  row.attrs:
#         # print(row)
#         if row.attrs["class"] == "over_header":
#             continue
#     else:
#         for column in row.find_all('th'):
#             if "data-over-header" in column.attrs:
#                 data.setdefault(column.attrs["data-stat"],"{}☳{}".format(column.attrs["data-over-header"],column.text))
#                 print(column.attrs["data-stat"],"{}☳{}".format(column.attrs["data-over-header"],column.text))
#             else:
#                 data.setdefault(column.attrs["data-stat"],"General☳{}".format(column.text))
#             # print(column)
#             # print("Text:{0}/ Span:{1}".format(column.text,column.attrs["data-over-header"]))
# print(data)
StatTitleRef = { 'year_id': 'General☳Year', 'game_date': 'General☳Date', 'game_num': 'General☳G#', 'week_num': 'General☳Week', 'age': 'General☳Age', 'team': 'General☳Tm', 'game_location': 'General☳Loc', 'opp': 'General☳Opp', 'game_result': 'General☳Result', 'gs': 'Games☳GS', 'pass_cmp': 'Passing☳Cmp', 'pass_att': 'Passing☳Att', 'pass_cmp_perc': 'Passing☳Cmp%', 'pass_yds': 'Passing☳Yds', 'pass_td': 'Passing☳TD', 'pass_int': 'Passing☳Int', 'pass_rating': 'Passing☳Rate', 'pass_sacked': 'Passing☳Sk', 'pass_sacked_yds': 'Passing☳Sk Yds', 'pass_yds_per_att': 'Passing☳Y/A', 'pass_adj_yds_per_att': 'Passing☳AY/A', 'rush_att': 'Rushing☳Att', 'rush_yds': 'Rushing☳Yds', 'rush_yds_per_att': 'Rushing☳Y/A', 'rush_td': 'Rushing☳TD', 'targets': 'Receiving☳Tgt', 'rec': 'Receiving☳Rec', 'rec_yds': 'Receiving☳Yds', 'rec_yds_per_rec': 'Receiving☳Y/R', 'rec_td': 'Receiving☳TD', 'catch_pct': 'Receiving☳Ctch%', 'rec_yds_per_tgt': 'Receiving☳Y/Tgt', 'two_pt_md': 'Scoring☳2PM', 'all_td': 'Scoring☳TD', 'scoring': 'Scoring☳Pts', 'sacks': 'General☳Sk', 'tackles_solo': 'Tackles☳Solo', 'tackles_assists': 'Tackles☳Ast', 'tackles_combined': 'Tackles☳Comb', 'tackles_loss': 'Tackles☳TFL', 'qb_hits': 'Tackles☳QBHits', 'fumbles': 'Fumbles☳Fmb', 'fumbles_lost': 'Fumbles☳FL', 'fumbles_forced': 'Fumbles☳FF', 'fumbles_rec': 'Fumbles☳FR', 'fumbles_rec_yds': 'Fumbles☳Yds', 'fumbles_rec_td': 'Fumbles☳TD', 'offense': 'Off. Snaps☳Num', 'off_pct': 'Off. Snaps☳Pct', 'defense': 'Def. Snaps☳Num', 'def_pct': 'Def. Snaps☳Pct', 'special_teams': 'ST Snaps☳Num', 'st_pct': 'ST Snaps☳Pct', 'status': 'General☳Status'}

# StatTitleRef = {'ranker': 'General☳Rk', 'year_id': 'General☳Year', 'game_date': 'General☳Date', 'game_num': 'General☳G#', 'week_num': 'General☳Week', 'age': 'General☳Age', 'team': 'General☳Tm', 'game_location': 'General☳Loc', 'opp': 'General☳Opp', 'game_result': 'General☳Result', 'gs': 'Games☳GS', 'pass_cmp': 'Passing☳Cmp', 'pass_att': 'Passing☳Att', 'pass_cmp_perc': 'Passing☳Cmp%', 'pass_yds': 'Passing☳Yds', 'pass_td': 'Passing☳TD', 'pass_int': 'Passing☳Int', 'pass_rating': 'Passing☳Rate', 'pass_sacked': 'Passing☳Sk', 'pass_sacked_yds': 'Passing☳Sk Yds', 'pass_yds_per_att': 'Passing☳Y/A', 'pass_adj_yds_per_att': 'Passing☳AY/A', 'rush_att': 'Rushing☳Att', 'rush_yds': 'Rushing☳Yds', 'rush_yds_per_att': 'Rushing☳Y/A', 'rush_td': 'Rushing☳TD', 'targets': 'Receiving☳Tgt', 'rec': 'Receiving☳Rec', 'rec_yds': 'Receiving☳Yds', 'rec_yds_per_rec': 'Receiving☳Y/R', 'rec_td': 'Receiving☳TD', 'catch_pct': 'Receiving☳Ctch%', 'rec_yds_per_tgt': 'Receiving☳Y/Tgt', 'two_pt_md': 'Scoring☳2PM', 'all_td': 'Scoring☳TD', 'scoring': 'Scoring☳Pts', 'sacks': 'General☳Sk', 'tackles_solo': 'Tackles☳Solo', 'tackles_assists': 'Tackles☳Ast', 'tackles_combined': 'Tackles☳Comb', 'tackles_loss': 'Tackles☳TFL', 'qb_hits': 'Tackles☳QBHits', 'fumbles': 'Fumbles☳Fmb', 'fumbles_lost': 'Fumbles☳FL', 'fumbles_forced': 'Fumbles☳FF', 'fumbles_rec': 'Fumbles☳FR', 'fumbles_rec_yds': 'Fumbles☳Yds', 'fumbles_rec_td': 'Fumbles☳TD', 'offense': 'Off. Snaps☳Num', 'off_pct': 'Off. Snaps☳Pct', 'defense': 'Def. Snaps☳Num', 'def_pct': 'Def. Snaps☳Pct', 'special_teams': 'ST Snaps☳Num', 'st_pct': 'ST Snaps☳Pct', 'status': 'General☳Status'}
# StatTitleRef = {"player":"General☳Player","split_id":"General☳Split","split_type":"General☳Split","split_value":"General☳Value","g":"Games☳G","wins":"Games☳W","losses":"Games☳L","ties":"Games☳T","pass_cmp":"Passing☳Cmp","pass_att":"Passing☳Att","pass_inc":"Passing☳Inc","pass_cmp_perc":"Passing☳Cmp%","pass_yds":"Passing☳Yds","pass_first_down":"Passing☳1D","pass_td":"Passing☳TD","pass_int":"Passing☳Int","pass_rating":"Passing☳Rate","pass_sacked":"Passing☳Sk","pass_sacked_yds":"Passing☳Yds","pass_yds_per_att":"Passing☳Y/A","pass_adj_yds_per_att":"Passing☳AY/A","pass_att_per_g":"Passing☳A/G","pass_yds_per_g":"Passing☳Y/G","rush_att":"Rushing☳Att","rush_yds":"Rushing☳Yds","rush_yds_per_att":"Rushing☳Y/A","rush_td":"Rushing☳TD","rush_att_per_g":"Rushing☳A/G","rush_yds_per_g":"Rushing☳Y/G","rush_first_down":"Rushing☳1D","all_td":"Scoring☳TD","scoring":"Scoring☳Pts","fumbles":"Fumbles☳Fmb","fumbles_lost":"Fumbles☳FL","fumbles_forced":"Fumbles☳FF","fumbles_rec":"Fumbles☳FR","fumbles_rec_yds":"Fumbles☳Yds","fumbles_rec_td":"Fumbles☳TD"}


# playersArr =[{"player":"Lamar Jackson","id":"JackLa00"},{"player":"Jared Goff","id":"GoffJa00"},{"player":"Russell Wilson","id":"WilsRu00"}]

playersArr =[{"player":"Lamar Jackson","id":"JackLa00"},{"player":"Jared Goff","id":"GoffJa00"},{"player":"Russell Wilson","id":"WilsRu00"},{"player":"Jameis Winston","id":"WinsJa00"},{"player":"Josh Allen","id":"AlleJo02"},{"player":"Sam Darnold","id":"DarnSa00"},{"player":"Joe Burrow","id":"BurrJo01"},{"player":"Baker Mayfield","id":"MayfBa00"},{"player":"Jayden Daniels","id":"DaniJa02"},{"player":"Joe Flacco","id":"FlacJo00"},{"player":"Derek Carr","id":"CarrDe02"},{"player":"Jalen Hurts","id":"HurtJa00"},{"player":"Justin Herbert","id":"HerbJu00"},{"player":"Kyler Murray","id":"MurrKy00"},{"player":"Kirk Cousins","id":"CousKi00"},{"player":"C.J. Stroud","id":"StroCJ00"},{"player":"Trevor Lawrence","id":"LawrTr00"},{"player":"Justin Fields","id":"FielJu00"},{"player":"Brock Purdy","id":"PurdBr00"},{"player":"Drake Maye","id":"MayeDr00"},{"player":"Jordan Love","id":"LoveJo03"},{"player":"Matthew Stafford","id":"StafMa00"},{"player":"Geno Smith","id":"SmitGe00"},{"player":"Tua Tagovailoa","id":"TagoTu00"},{"player":"Caleb Williams","id":"WillCa03"},{"player":"Aaron Rodgers","id":"RodgAa00"},{"player":"Patrick Mahomes","id":"MahoPa00"},{"player":"Dak Prescott","id":"PresDa01"},{"player":"Andy Dalton","id":"DaltAn00"},{"player":"Bo Nix","id":"NixxBo00"},{"player":"Gardner Minshew II","id":"MinsGa00"},{"player":"Daniel Jones","id":"JoneDa05"},{"player":"Deshaun Watson","id":"WatsDe00"},{"player":"Aidan O'Connell","id":"OConAi00"},{"player":"Jacoby Brissett","id":"BrisJa00"},{"player":"Tyler Huntley","id":"HuntTy01"},{"player":"Will Levis","id":"LeviWi00"},{"player":"Spencer Rattler","id":"RattSp00"},{"player":"Mason Rudolph","id":"RudoMa00"},{"player":"Bryce Young","id":"YounBr01"},{"player":"Anthony Richardson","id":"RichAn03"}]  
# for player in playersArr:
#     url = 'https://www.pro-football-reference.com/players/{0}/{1}/gamelog'.format(player["id"][0],player['id'])
#     time.sleep(5)
#     splits = soup(requests.get(url).text, 'html.parser')
#     table = splits.find('table', id="stats")
#     GetHeaders(table)
#     for row in table.tbody.findAll('tr'):
#         first_column = row.findAll('th')[0]
#         if first_column.text == "Rk":
#             continue
#         # data.setdefault("General☳Player",[]).append(player["player"]
#         # firstAttr = first_column.attrs["data-stat"]
#         # if firstAttr in StatTitleRef:
#         #     firstAttr = StatTitleRef[firstAttr]
#         #     data.setdefault(firstAttr,[]).append(first_column.text)
#         for cell in row.findAll('td'):
#             attr = cell.attrs["data-stat"]
#             if attr == "reason":
#                 continue
#             if attr in StatTitleRef:
#                 attr = StatTitleRef[attr]
#             data.setdefault(attr,[]).append(cell.text)
#         for key in data:
#             # print("General",len(data["General☳Year"]), key,len(data[key]))
#             if len(data["General☳Year"]) != len(data[key]):
#                 data[key].append("")     
#     lens = map(len, data.values())
#     if len(set(lens)) == 1:
#         print("{0} completed".format(player["player"]))
#         df = pd.DataFrame(data)
#         df.columns = pd.MultiIndex.from_tuples([tuple(c.split("☳")) for c in df.columns])
#         dataframes.setdefault(player["player"],df)
#         # df.to_excel("/Users/avatara/Documents/Web Scraping/QB Game Logs/{}.csv".format(player["player"]), index=False) 
#         data.clear()
#     else:
#         print("{0} ERROR".format(player["player"]))
#         exit()

# save_xls(dataframes,"logs.xlsx")




# def format_title(attr):
#     if "pass_" in attr:
#         attr = attr.replace("pass_","Passing☳")
#     if "rush_" in attr:
#         attr = attr.replace("rush_","Rushing☳")
#     if "split_" in attr:
#         attr = attr.replace("split_","General☳")
#     attrArr = attr.split("☳")
#     attrCat = attrArr[0]
#     attrVal = attrArr[1]
#     attrVal.replace("cmp perc")
    
    
