import numpy as np
import cfbd

#----------------Grab data from API, save as string "games"-----------------

configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = 'INSERT AUTHENTICATION STRING HERE'  #Grab an authentication string from "https://collegefootballdata.com/key#google_vignette"
configuration.api_key_prefix['Authorization'] = 'Bearer'


api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
games = api_instance.get_games(year=2024)

home_teams = []
away_teams = []
home_pts = []
away_pts = []
week = []

Teams_list = []

#-----------------------Scrape Info from string "games"------------------------

games_arrTEMP = str(games).split("'home_team': ")
i=1
while i<len(games):
    home_teams.append(games_arrTEMP[i].split(",")[0].replace("'","").replace('"',''))
    i = i + 1

games_arrTEMP = str(games).split("'away_team': ")
i=1
while i<len(games):
    away_teams.append(games_arrTEMP[i].split(",")[0].replace("'","").replace('"',''))
    i = i + 1

games_arrTEMP = str(games).split("'home_points': ")
i=1
while i<len(games):
    try:
        home_pts.append(int(float(games_arrTEMP[i].split(",")[0])))
    except:
        home_pts.append(games_arrTEMP[i].split(",")[0])
    i = i + 1

games_arrTEMP = str(games).split("'away_points': ")
i=1
while i<len(games):
    try:
        away_pts.append(int(float(games_arrTEMP[i].split(",")[0])))
    except:
        away_pts.append(games_arrTEMP[i].split(",")[0])
    i = i + 1

games_arrTEMP = str(games).split("'week': ")
i=1
while i<len(games):
    week.append(games_arrTEMP[i].split("}")[0].replace("'","").replace('"',''))
    i = i + 1

#---------Take the teams scraped and put them in a list-----------

for a in home_teams:
    if a not in Teams_list:
        Teams_list.append(a)
for a in away_teams:
    if a not in Teams_list:
        Teams_list.append(a)

#----------------------Build the Matricies------------------------

numMatches = len(home_teams)
matrix1 = np.array([[0 for x in range(len(Teams_list))] for y in range(numMatches)])
matrixWL = np.array([0 for x in range(numMatches)])
Wins = np.array([0 for x in range(len(Teams_list))])
Losses = np.array([0 for x in range(len(Teams_list))])
i = 0
while i < numMatches:
    weight = 1
    if home_pts == None or away_pts == None:    #Makes sure to exclude unplayed matches
        weight = 0
    if week[i]=='14':                           #Excludes conference championships. Remove this if you want to include them
        weight = 0
    matrix1[i][Teams_list.index(home_teams[i])] = weight
    matrix1[i][Teams_list.index(away_teams[i])] = -weight

    if home_pts[i] > away_pts[i]:
        matrixWL[i] = weight
        Wins[Teams_list.index(home_teams[i])] += 1
        Losses[Teams_list.index(away_teams[i])] += 1
    elif home_pts[i] < away_pts[i]:
        matrixWL[i] = -weight
        Wins[Teams_list.index(away_teams[i])] += 1
        Losses[Teams_list.index(home_teams[i])] += 1
    i = i + 1

#--------------------Solve the Matrix------------------------

d = np.linalg.lstsq(matrix1, matrixWL, rcond=None)[0]

#---Put strength values in terms of standard deviations from the mean---

dstd = np.std(d)
dmean = np.mean(d)
d = (d - dmean) / dstd

#-----------------------Print top 100 teams------------------------

i=0
higher=99999
j=1
TopIndex = 0
Top = -999999
while j<=100:                                                           #outputs top 100 in order
    while i<len(Teams_list):
        if d[i]>Top:
            if d[i]<higher:
                Top = d[i]
                TopIndex=i
        i+=1

    print(str(j)+".  "+str(Teams_list[TopIndex])+"  ("+str(Wins[TopIndex])+"-"+str(Losses[TopIndex])+")    "+str(round(d[TopIndex],5)))
    j=j+1
    i=0
    higher=Top
    Top=-99999
