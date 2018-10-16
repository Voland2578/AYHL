import requests
from bs4 import BeautifulSoup
import pdb
from collections import namedtuple
import xlsxwriter

# representation of the game
Game = namedtuple('Game', 'game_id home_team away_team date link')
# Game result object
GameResult = namedtuple('GameResult', 'game_obj away_penalties home_penalties away_goalies home_goalies away_goals home_goals')
# representation of the goals
Goal = namedtuple('Goal', 'game_id team player assist1 assist2 period time goal_type')
# penalties
Penalty = namedtuple('Penalty', 'game_id team player period penalty_time penalty_minutes penalty_type')
# goalie
Goalie = namedtuple('Goalie', 'game_id team goalie minutes_played saves shots pct')



def getPlayerFromTd(td):
    link = td.find("a")
    if link is None:
        return td.contents[0].strip()
    return link.contents[0]


def contents(cell):
    return cell.contents[0]


def visitGoalie(recap_table, game, team, opponent_team):
    # skip header row
    all_rows = iter(recap_table.find_all("tr"))
    next(all_rows)

    all_goalies = []
    for next_row in all_rows:
        cells = next_row.find_all("td")

        goalie = getPlayerFromTd(cells[0])
        minutes_played = int(contents(cells[1]))
        saves = int (contents(cells[2]))
        shots = int( contents(cells[3]))
        pct = contents(cells[4])

        all_goalies.append(Goalie(game.game_id, team, goalie, minutes_played, saves, shots, pct))
    return all_goalies


def visitGoalRecap(recap_table, game, team):
    # skip header row
    all_rows = iter(recap_table.find_all("tr"))
    next(all_rows)

    all_goals = []
    for next_row in all_rows:
        cells = next_row.find_all("td")
        player = getPlayerFromTd(cells[0])
        assist1 = getPlayerFromTd(cells[1])
        assist2 = getPlayerFromTd(cells[2])
        period = contents(cells[3])
        time = contents(cells[4])
        goal_type = contents(cells[5])

        all_goals.append(Goal(game.game_id, team, player, assist1, assist2, period, time, goal_type))
    return all_goals


def visitPenaltyRecap(penalty_table, game, team):
    # skip header row
    all_rows = iter(penalty_table.find_all("tr"))
    next(all_rows)

    all_penalties = []
    for next_row in all_rows:
        cells = next_row.find_all("td")
        try:
            player = getPlayerFromTd(cells[0])
            period = contents(cells[1])
            penalty_time = contents(cells[2])
            penalty_minutes = int(contents(cells[3]).split(":")[0])
            penalty_type = contents(cells[4])
            all_penalties.append(
                Penalty(game.game_id, team, player, period, penalty_time, penalty_minutes, penalty_type))
        except:
            # hard to process bad html at times
            pass
    return all_penalties

def countAssists(goals_summary):
    return sum ([ 1 if n is not None else 0 for n in [goals_summary.assist1, goals_summary.assist2] ])

# Visit sections of interest
def visitOneGame(game):
    print("Game URI: {}".format(game.link))
    game_page = requests.get(game_uri)
    game_soup = BeautifulSoup(game_page.content, "html.parser")

    recap_tables = game_soup.find_all("table", class_="recap_table")

    # goals
    away_goals = visitGoalRecap(recap_tables[0], game, game.away_team)
    home_goals = visitGoalRecap(recap_tables[1], game, game.home_team)

    # penalties
    away_penalties = visitPenaltyRecap(recap_tables[2], game, game.away_team)
    home_penalties = visitPenaltyRecap(recap_tables[3], game, game.home_team)

    # goalies
    away_goalies = visitGoalie(recap_tables[8], game, game.away_team, game.home_team)
    home_goalies = visitGoalie(recap_tables[9], game, game.home_team, game.away_team)

    gr = GameResult(game, away_penalties, home_penalties, away_goalies, home_goalies,
                    away_goals, home_goals
                    )

    return gr

def updateTeamResult(resultMap, team, player , statisticKey, startValue, addValue):
    updateResult(resultMap, team, team, statisticKey, startValue, addValue)

def updateResult(resultMap, team, player , statisticKey, startValue, addValue):
    if player is None or player == '-':
        return

    key = "{}_{}".format(team, player)
    if not key in resultMap:
        resultMap[key]={}
        resultMap[key][statisticKey] = startValue

    player_map = resultMap[key]
    # get data for the statkey
    if not statisticKey in player_map:
        player_map[statisticKey] = startValue

    player_map[statisticKey] = player_map[statisticKey] + addValue


def dumpScoringData(workbook, results):
    scoreWorksheet = workbook.add_worksheet('ScoringAndAssists')
    headers = [ "Team", "Name", "Goals", "Assists", "Penalty_Minutes"]
    row  =  0

    result = {}
    # map of results, keyed on team+player
    for idx, val in enumerate(headers):
        scoreWorksheet.write(0, idx, val)

    for next_game in results:
        processed_players = []
        for game_scoring in next_game.home_goals + next_game.away_goals:
             updateResult(result, game_scoring.team, game_scoring.player, "goal",0,1)
             updateResult(result, game_scoring.team, game_scoring.assist1, "assist",0,1)
             updateResult(result, game_scoring.team, game_scoring.assist2, "assist",0,1)

             processed_players.append((game_scoring.team, game_scoring.player))
             processed_players.append((game_scoring.team, game_scoring.assist1))
             processed_players.append((game_scoring.team, game_scoring.assist2))

        for game_penalties in next_game.home_penalties + next_game.away_penalties:
            updateResult(result, game_penalties.team, game_penalties.player, "penalty_min", 0,  int (game_penalties.penalty_minutes))
            processed_players.append((game_penalties.team, game_penalties.player))

        # count games played for each player
        list(map(lambda p: updateResult(result, p[0], p[1], "games",0,1), filter(lambda x: x[1] != '-', processed_players)))


    row = 1
    for i,( key, next_player) in enumerate(result.items()):
        (team, player) = key.split("_")

        for idx,value in enumerate([ team, player, next_player.get('goal',0), next_player.get('assist',0 ), next_player.get('penalty_min',0 )
                                       #,next_player.get('games',0 )
                                   ]):
            scoreWorksheet.write(row, idx, value)
        row = row + 1

# dump game data
def dumpGameData(workbook, results):
    game_worksheet = workbook.add_worksheet('Games')
    summary_worksheet = workbook.add_worksheet('Summary')
    summary_headers = [ "Team", "Games", "Wins", "Losses", "Ties", "Shots", "Goals", "Assists", "Shots_Against", "Goals_Against","Penalty_Minutes"]
    game_headers = ["Date", "Home","Away","Home Goals", "Away Goals", "Link"]
    result = {}
    row = 1

    for idx, val in enumerate(summary_headers):
        summary_worksheet.write(0, idx, val)

    for idx, val in enumerate(game_headers):
        game_worksheet.write(0, idx, val)


    for next_game in results:
        game = next_game.game_obj;

        updateTeamResult(result, game.away_team, None, "games", 0, 1)
        updateTeamResult(result, game.home_team, None, "games", 0, 1)

        if (len(next_game.away_goals) > len(next_game.home_goals)):
            updateTeamResult(result, game.away_team, None, "wins", 0, 1)
            updateTeamResult(result, game.home_team, None, "losses", 0, 1)
        elif len(next_game.home_goals) > len(next_game.away_goals):
            updateTeamResult(result, game.away_team, None, "losses", 0, 1)
            updateTeamResult(result, game.home_team, None, "wins", 0, 1)
        else:
            updateTeamResult(result, game.away_team, None, "ties", 0, 1)
            updateTeamResult(result, game.home_team, None, "ties", 0, 1)

        updateTeamResult(result, game.away_team, None, "goals", 0, len(next_game.away_goals))
        updateTeamResult(result, game.home_team, None, "goals", 0, len(next_game.home_goals))

        updateTeamResult(result, game.away_team, None, "sog", 0, sum([x.shots for x in next_game.home_goalies]))
        updateTeamResult(result, game.home_team, None, "sog", 0, sum([x.shots for x in next_game.away_goalies]))

        updateTeamResult(result, game.away_team, None, "assists", 0, sum ([ countAssists(x) for x in next_game.away_goals]))
        updateTeamResult(result, game.home_team, None, "assists", 0, sum ([ countAssists(x) for x in next_game.home_goals]))

        updateTeamResult(result, game.away_team, None, "penalty_minutes", 0, sum([x.penalty_minutes for x in next_game.away_penalties]))
        updateTeamResult(result, game.home_team, None, "penalty_minutes", 0, sum([x.penalty_minutes for x in next_game.home_penalties]))

        updateTeamResult(result, game.away_team, None, "shots_against", 0, sum([x.shots for x in next_game.away_goalies]))
        updateTeamResult(result, game.home_team, None, "shots_against", 0, sum([x.shots for x in next_game.home_goalies]))

        updateTeamResult(result, game.away_team, None, "goals_against", 0, sum([x.shots - x.saves for x in next_game.away_goalies]))
        updateTeamResult(result, game.home_team, None, "goals_against", 0, sum([x.shots - x.saves for x in next_game.home_goalies]))

        game_data = [ game.date, game.home_team, game.away_team, len(next_game.home_goals), len(next_game.away_goals), next_game.game_obj.link]
        for i, x in enumerate(game_data):
            game_worksheet.write(row, i, x)
        row = row + 1

    row  = 1
    for i,( team, data) in enumerate(result.items()):
        (team, player) = team.split("_")
        summary_worksheet.write(row, 0, team)
        for idx,value in enumerate([ "games", "wins", "losses","ties", "sog", "goals", "assists","shots_against","goals_against","penalty_minutes" ]):
            summary_worksheet.write(row, idx+1, data.get(value,0))
        row = row + 1

# dump goalie data
def dumpGoalieData(workbook, results):
    goaliesWorksheet = workbook.add_worksheet('Goalies')
    headers = [ "Team", "Name", "Shots", "Saves","PCT","MinPlayed","GamesPlayed"]
    result = {}

    row  =  0
    for idx, val in enumerate(headers):
        goaliesWorksheet.write(0, idx, val)

    row = 1
    for next_game in results:
        home_goalies = next_game.home_goalies
        away_goalies = next_game.away_goalies
        for goalie in home_goalies + away_goalies:
           updateResult(result, goalie.team, goalie.goalie, "shots",0, goalie.shots)
           updateResult(result, goalie.team, goalie.goalie, "saves", 0, goalie.saves)
           updateResult(result, goalie.team, goalie.goalie, "minutes_played", 0, int(goalie.minutes_played))
           updateResult(result, goalie.team, goalie.goalie, "games_played", 0, 1)

    for i,( key, next_player) in enumerate(result.items()):
        (team, player) = key.split("_")

        for idx,value in enumerate([ team, player, next_player.get('shots',0), next_player.get('saves',0 ),
                                     next_player.get('saves', 0) / next_player.get('shots',0 ),
                                     next_player.get('minutes_played',0 ), next_player.get('games_played',0 ) ]):
            goaliesWorksheet.write(row, idx, value)
        row = row + 1



# dump scoring data



base_uri = 'http://atlantichockey.org'

if __name__ == "__main__":
    query_map = {}
    query_map['titans_08.xlsx'] = '{}/scores.php?leagueid=213&seasonid=25&dateid=99'.format(base_uri)
    #query_map['titans_06.xlsx'] = '{}/scores.php?leagueid=215&seasonid=25&dateid=99'.format(base_uri)

    for (output_file, next_team_uri) in query_map.items():
        print ("Accessing: {}".format(next_team_uri))
        page = requests.get(next_team_uri)
        soup = BeautifulSoup(page.content, 'html5lib')

        # get results table
        results_table = soup.find(name="table", class_='results')
        row_count = 0
        results = []

        for row in results_table.find_all("tr"):
            # find the table-row class which corresponds to the recap link
            # skip the first row
            row_count = row_count + 1
            if row_count == 1:
                continue;

            recap_link = row.find("td", class_="table-row")
            tds = row.find_all("td")
            # game id
            game_id = tds[0].next
            # away_team
            away_team = tds[2].find("a").next.strip()
            # home team
            home_team = tds[3].find("a").next.strip()
            # date
            date = tds[4].next.strip()
            # link uri
            link = recap_link.find("a").attrs["href"]
            game_uri = "{}/{}".format(base_uri, link)

            results.append(visitOneGame(Game(game_id, home_team, away_team, date, game_uri)))

        workbook = xlsxwriter.Workbook('D:\\{}'.format(output_file))
        dumpGameData(workbook, results)
        dumpGoalieData(workbook, results)
        dumpScoringData(workbook, results)
        workbook.close()
