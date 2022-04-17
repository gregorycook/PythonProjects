#/usr/bin/env/python3

import json
import os
import random
import time
import uuid

from datetime import datetime
from ftplib import FTP
from lxml import html

import requests

session_id = uuid.uuid1()
headers = {
    'Cache-Control': 'private, max-age=0, no-cache',
    "Pragma": "no-cache",
    "Expires": "Thu, 01 Jan 1970 00:00:00 GMT",
    "SessionId": str(session_id)
}

time.sleep(15)

DATA_FILE_PATH = "/home/pi/Project/PythonProjects/Baseball2022/data/{}.json"

# baseball reference keys
player_br = {
    "Crawford": "crawfjp01.shtml",
    "Sewald": "sewalpa01.shtml",
    "Gilbert": "gilbelo01.shtml",
    "Ray": "rayro02.shtml",
    "Frazier": "fraziad01.shtml",
    "Toro": "toroab01.shtml",
    "Flexen": "flexech01.shtml",
    "Brash": "brashma01.shtml",
    "Murphy": "murphto04.shtml",
    "Raleigh": "raleica01.shtml",
    "Rodriguez": "rodriju01.shtml",
    "Suarez": "suareeu01.shtml",
    "France": "francty01.shtml",
    "Haniger": "hanigmi01.shtml",
    "Winker": "winkeje01.shtml",
    "Kelenic": "kelenja01.shtml",
    "Gonzales": "gonzama02.shtml",
    "Lewis": "lewisky01.shtml",
    "Castillo": "castidi01.shtml",
    "Moore": "mooredy01.shtml"
}

teams = {
    "Gregory": [
        (1, "Crawford", "J.P. Crawford"),
        (4, "Gilbert", "Logan Gilbert"),
        (5, "Ray", "Robbie Ray"),
        (8, "Frazier", "Adam Frazier"),
        (9, "Toro", "Abraham Toro"),
        (12, "Flexen", "Chris Flexen"),
        (13, "Brash", "Matt Brash"),
        (16, "Murphy", "Tom Murphy"),
        (17, "Raleigh", "Cal Raleigh"),
        (20, "Sewald", "Paul Sewald"),
    ],
    "Hans": [
        (2, "Rodriguez", "Julio Rodriguez"),
        (3, "France", "Ty France"),
        (6, "Haniger", "Mitch Haniger"),
        (7, "Winker", "Jesse Winker"),
        (10, "Kelenic", "Jarred Kelenic"),
        (11, "Gonzales", "Marco Gonzales"),
        (14, "Lewis", "Kyle Lewis"),
        (15, "Castillo", "Diego Castillo"),
        (18, "Moore", "Dylan Moore"),
        (19, "Suarez", "Eugenio Suarez"),
    ]
}


def get_standard_stat(player, stat_name, stat_type):
    player_key = player_br[player]
    main_player_page = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fplayers%2F{}%2F{}&div=div_{}_standard"
    standard_stat_xpath = "string(//tr[@id='{}_standard.2022']/td[@data-stat='{}'])"

    site = main_player_page.format(player_key[0], player_key, stat_type)
    page = requests.get(site, headers)
    tree = html.fromstring(page.text)
    value = tree.xpath(standard_stat_xpath.format(stat_type, stat_name))
    if len(value) > 0:
        return float(value)

    return 0


def get_value_stat(player, stat_name, stat_type):
    player_key = player_br[player]
    player_value_site = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fplayers%2F{}%2F{}&div=div_{}_value"
    value_stat_xpath = '//tr[@id="{}_value.2022"]/td[@data-stat="{}"]/text()'

    site = player_value_site.format(player_key[0], player_key, stat_type)
    page = requests.get(site, headers)
    thing = []
    try:
        table_index = str.index(page.text, "<table")
        end_table_index = str.index(page.text, "</table")
        end_table_index = str.index(page.text, ">", end_table_index)
        table_element = page.text[table_index:end_table_index + 1]
        table_element = table_element.replace("&rsquo;", "")
        tree = html.fromstring(table_element)
        specific_xpath = value_stat_xpath.format(stat_type, stat_name)
        thing = tree.xpath(specific_xpath)
    except Exception as e:
        pass
    value = 0
    if len(thing) > 0:
        value = float(thing[0])

    return value


def get_mariners_no_hit():
    site = 'https://www.nonohitters.com/no-hitters-against-the-seattle-mariners/'
    xpath = 'count(//table[@class="nonolist"]/tbody/tr/th[number(text())>0])'
    page = requests.get(site, headers)
    tree = html.fromstring(page.text)
    value = tree.xpath(xpath)

    return value - 5


def get_pitcher_count():
    mariners_team_pitching_site = 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fteams%2FSEA%2F2022.shtml&div=div_team_pitching'
    mariners_pitcher_count_xpath = "count(//table[@id='team_pitching']//tr[number(td[@data-stat='IP']/text()) > 0])"
    site = mariners_team_pitching_site
    page = requests.get(site, headers)
    tree = html.fromstring(page.text)
    value = tree.xpath(mariners_pitcher_count_xpath) - 2

    return value


def get_mariners_record():
    record_site = "https://www.baseball-reference.com/"
    record_xpath_wins = "//table[@id='standings_AL']//tr[th/@csk='SEA']//td[@data-stat='W']/text()"
    record_xpath_losses = "//table[@id='standings_AL']//tr[th/@csk='SEA']//td[@data-stat='L']/text()"

    # lookup wins/losses
    page = requests.get(record_site, headers)
    tree = html.fromstring(page.text)
    wins = int(tree.xpath(record_xpath_wins)[0])
    losses = int(tree.xpath(record_xpath_losses)[0])

    return wins, losses


def get_mariners_runs():
    baseball_reference_mariners_site = "https://www.baseball-reference.com/teams/SEA/2022.shtml"
    runs_scored_allowed_xpath = "//div[@data-template='Partials/Teams/Summary']//p[a/strong/text()='Pythagorean W-L:']/text()"

    # lookup runs scored/allowed
    page = requests.get(baseball_reference_mariners_site, headers)
    tree = html.fromstring(page.text)
    summary_text = tree.xpath(runs_scored_allowed_xpath)

    runs_scored = 1
    runs_allowed = 1
    if len(summary_text):
        summary_list = summary_text[-1].split(",")
        runs_scored_text = summary_list[1]
        runs_allowed_text = summary_list[2]
        runs_scored = float(runs_scored_text[:runs_scored_text.index('Runs')])
        runs_allowed = float(runs_allowed_text[:runs_allowed_text.index('Runs')])

    return runs_scored, runs_allowed


def get_stat_dict():
    stat_dict = dict()

    # G1
    stat_dict["Crawford"] = {}
    stat_dict["Crawford"]["WAR"] = get_value_stat("Crawford", "WAR", "batting")

    # G2
    stat_dict["Gilbert"] = {}
    stat_dict["Gilbert"]["WAR"] = get_value_stat("Gilbert", "WAR_pitch", "pitching")
    stat_dict["Gilbert"]["ERA"] = get_standard_stat("Gilbert", "earned_run_avg", "pitching")

    # G3
    stat_dict["Ray"] = {}
    stat_dict["Ray"]["WAR"] = get_value_stat("Ray", "WAR_pitch", "pitching")

    # G4
    stat_dict["Frazier"] = {}
    stat_dict["Frazier"]["WAR"] = get_value_stat("Frazier", "WAR", "batting")
    stat_dict["Frazier"]["HRs"] = get_standard_stat("Frazier", "HR", "batting")

    # G5
    stat_dict["Toro"] = {}
    stat_dict["Toro"]["WAR"] = get_value_stat("Toro", "WAR", "batting")

    # G6
    stat_dict["Flexen"] = {}
    stat_dict["Flexen"]["WAR"] = get_value_stat("Flexen", "WAR_pitch", "pitching")

    # G7
    stat_dict["Brash"] = {}
    stat_dict["Brash"]["WAR"] = get_value_stat("Brash", "WAR_pitch", "pitching")

    # G8
    stat_dict["Murphy"] = {}
    stat_dict["Murphy"]["HRs"] = get_standard_stat("Murphy", "HR", "batting")
    stat_dict["Murphy"]["WAR"] = get_value_stat("Murphy", "WAR", "batting")

    # G9
    stat_dict["Raleigh"] = {}
    stat_dict["Raleigh"]["WAR"] = get_value_stat("Raleigh", "WAR", "batting")

    # G10
    stat_dict["Sewald"] = {}
    stat_dict["Sewald"]["WAR"] = get_value_stat("Sewald", "WAR_pitch", "pitching")

    # H1
    stat_dict["Rodriguez"] = {}
    stat_dict["Rodriguez"]["WAR"] = get_value_stat("Rodriguez", "WAR", "batting")
    stat_dict["Rodriguez"]["OPS"] = get_standard_stat("Rodriguez", "onbase_plus_slugging", "batting")
    stat_dict["Rodriguez"]["HRs"] = get_standard_stat("Rodriguez", "HR", "batting")

    # H2
    stat_dict["France"] = {}
    stat_dict["France"]["WAR"] = get_value_stat("France", "WAR", "batting")

    # H3
    stat_dict["Haniger"] = {}
    stat_dict["Haniger"]["HRs"] = get_standard_stat("Haniger", "HR", "batting")
    stat_dict["Haniger"]["WAR"] = get_value_stat("Haniger", "WAR", "batting")

    # H4
    stat_dict["Winker"] = {}
    stat_dict["Winker"]["WAR"] = get_value_stat("Winker", "WAR", "batting")

    # H5
    stat_dict["Kelenic"] = {}
    stat_dict["Kelenic"]["OPS"] = get_standard_stat("Kelenic", "onbase_plus_slugging", "batting")
    stat_dict["Kelenic"]["WAR"] = get_value_stat("Kelenic", "WAR", "batting")
    stat_dict["Kelenic"]["HRs"] = get_standard_stat("Kelenic", "HR", "batting")

    # H6
    stat_dict["Gonzales"] = {}
    stat_dict["Gonzales"]["ERA"] = get_standard_stat("Gonzales", "earned_run_avg", "pitching")
    stat_dict["Gonzales"]["WAR"] = get_value_stat("Gonzales", "WAR_pitch", "pitching")

    # H7
    stat_dict["Lewis"] = {}
    stat_dict["Lewis"]["WAR"] = get_value_stat("Lewis", "WAR", "batting")

    # H8
    stat_dict["Castillo"] = {}
    stat_dict["Castillo"]["WAR"] = get_value_stat("Castillo", "WAR", "batting")

    # H9
    stat_dict["Moore"] = {}
    stat_dict["Moore"]["WAR"] = get_value_stat("Moore", "WAR", "batting")

    # H10
    stat_dict["Suarez"] = {}
    stat_dict["Suarez"]["WAR"] = get_value_stat("Suarez", "WAR", "batting")
    stat_dict["Suarez"]["HRs"] = get_standard_stat("Suarez", "HR", "batting")

    stat_dict["Mariners"] = {}
    stat_dict["Mariners"]["PitcherCount"] = get_pitcher_count()
    stat_dict["Mariners"]["NoHitCount"] = get_mariners_no_hit()
    stat_dict["Mariners"]["Wins"], stat_dict["Mariners"]["Losses"] = get_mariners_record()
    stat_dict["Mariners"]["RunsScored"], stat_dict["Mariners"]["RunsAllowed"] = get_mariners_runs()

    return stat_dict


def my_round(value, places):
    if places == 0:
        return int(value)
    else:
        return round(float(value)*10**places)/10**places


def maybe_bold(over_under, name, value, target):
    if over_under == "Under" and value < target:
        return "<b>" + name + "</b>"
    elif over_under == "Over" and value > target:
        return "<b>" + name + "</b>"
    else:
        return name


def get_team_tables(new_stats, old_stats):
    team_tables = []
    team_number = 0
    for team in teams:
        team_number = team_number + 1
        total_war = 0
        table = "<div style='grid-column: {}; grid-row: 1;'><p class='team-text'>Team {}</p>\r\n<table class='team_table'>\r\n\t<thead><tr>\r\n\t\t<td>Pick</td>\r\n\t\t<td>Name</td>\r\n\t\t<td>WAR</td>\r\n\t\t<td></td>\r\n\t</tr></thead>".format(str(team_number), team)
        high_war = -10
        for player in teams[team]:
            war = new_stats[player[1]]["WAR"]
            if war > high_war:
                high_war = war
        for player in teams[team]:
            war = new_stats[player[1]]["WAR"]
            old_war = old_stats[player[1]]["WAR"]
            total_war = total_war + war
            war_delta = war - old_war
            war_delta_text = "" if war_delta == 0 else "({:.1f})".format(war_delta)
            war_column_class = "normal"
            if war == high_war:
                war_column_class = "bold"
            player_html = "<a target='_blank' href='https://www.baseball-reference.com/players/{}/{}'>{}</a>".format(player[1][0].lower(),  player_br[player[1]], player[2])
            row = "\r\n\t<tr>\r\n\t\t<td>{}</td>\r\n\t\t<td>{}</td>\r\n\t\t<td class='{}' align='right'>{:.1f}</td><td>{}</td>\r\n\t</tr>".format(player[0], player_html, war_column_class, war, war_delta_text)
            table = table + row

        new_stats["Mariners"][team] = total_war
        war_delta = total_war - old_stats["Mariners"][team]
        war_delta_text = "" if war_delta == 0 else "({:.1f})".format(war_delta)
        table = table + "</table>\r\n<p/>Total War: {:.1f} {}<p/></div>".format(total_war, war_delta_text)
        team_tables.append(table)

    return "<p/>".join(team_tables)


def get_projected_record_table(stats):
    pythagorean_power = 1.83

    # lookup wins/losses
    wins = stats["Mariners"]["Wins"]
    losses = stats["Mariners"]["Losses"]

    # lookup runs scored/allowed
    runs_scored = stats["Mariners"]["RunsScored"]
    runs_allowed = stats["Mariners"]["RunsAllowed"]
    pythagorean_percent = runs_scored**pythagorean_power/(runs_scored**pythagorean_power + runs_allowed**pythagorean_power)
    projected_wins = wins + pythagorean_percent*(162-wins-losses)
    stats["Mariners"]["ProjectedWins"] = projected_wins
    return "<table class='team_table'>\r\n<tr>" \
           "<td>Wins</td>" \
           "<td>Losses</td>" \
           "<td>Runs Scored</td>" \
           "<td>Runs Allowed</td>" \
           "<td>Pythagorean Win %</td>" \
           "<td>Projected Wins</td>" \
           "</tr>\r\n<tr>" \
           "<td>{:.0f}</td>" \
           "<td>{:.0f}</td>" \
           "<td>{:.0f}</td>" \
           "<td>{:.0f}</td>" \
           "<td>{:.1f}%</td>" \
           "<td>{:.1f}</td><" \
           "/tr>\r\n</table>".format(wins, losses, runs_scored, runs_allowed, 100*pythagorean_percent, projected_wins)


def get_total_negative_war(stats):
    result = 0
    for team in teams:
        for player in teams[team]:
            if stats[player[1]]["WAR"] < 0:
                result += 1

    return result


def get_over_under_table(stats):
    over_unders = {
        "Wins": {
            "Title": "Wins",
            "Value": 87.5,
            "Over": "Gregory",
            "Under": "Hans",
            "Rounding": (0, 1)
        },
        "PitcherCount": {
            "Title": "# of pitchers used",
            "Value": 32.5,
            "Over": "Gregory",
            "Under": "Hans",
            "Rounding": (0, 1)
        },
        "KelenicOPS": {
            "Title": "Kelenic OPS",
            "Value": 0.800,
            "Over": "Gregory",
            "Under": "Hans",
            "Rounding": (3, 3)
        },
        "RodriguezOPS": {
            "Title": "Rodriguez OPS",
            "Value": 0.815,
            "Over": "Hans",
            "Under": "Gregory",
            "Rounding": (3, 3)
        },
        "GilbertERA": {
            "Title": "Gilbert ERA",
            "Value": 3.5,
            "Over": "Gregory",
            "Under": "Hans",
            "Rounding": (2, 2)
        },
        "OldHomers": {
            "Title": "Homers by Old Guys",
            "Value": 69.5,
            "Over": "Gregory",
            "Under": "Hans",
            "Rounding": (0, 1)
        },
        "YoungHomers": {
            "Title": "Homers by Young Guys",
            "Value": 35.5,
            "Over": "Hans",
            "Under": "Gregory",
            "Rounding": (0, 1)
        }
    }

    wins = stats["Mariners"]["Wins"]
    losses = stats["Mariners"]["Losses"]

    over_unders["Wins"]["Current"] = stats["Mariners"]["Wins"]
    over_unders["Wins"]["Projected"] = stats["Mariners"]["ProjectedWins"]

    # total_negative_war = get_total_negative_war(stats)
    # over_unders["NegativeWAR"]["Current"] = total_negative_war
    # over_unders["NegativeWAR"]["Projected"] = total_negative_war
    # html_text = html_text.replace("<NegativeWARCount/>", "{:.0f}".format(total_negative_war))

    pitcher_count = stats["Mariners"]["PitcherCount"]
    projected_pitcher_count = (pitcher_count-14) * (162 / (wins + losses)) + 14
    if projected_pitcher_count < 14:
        projected_pitcher_count = 14
    over_unders["PitcherCount"]["Current"] = pitcher_count
    over_unders["PitcherCount"]["Projected"] = projected_pitcher_count

    rodriguez_ops = stats["Rodriguez"]["OPS"]
    over_unders["RodriguezOPS"]["Current"] = rodriguez_ops
    over_unders["RodriguezOPS"]["Projected"] = rodriguez_ops

    kelenic_ops = stats["Kelenic"]["OPS"]
    over_unders["KelenicOPS"]["Current"] = kelenic_ops
    over_unders["KelenicOPS"]["Projected"] = kelenic_ops

    gilbert_era = stats["Gilbert"]["ERA"]
    over_unders["GilbertERA"]["Current"] = gilbert_era
    over_unders["GilbertERA"]["Projected"] = gilbert_era

    haniger_hrs = stats["Haniger"]["HRs"]
    frazier_hrs = stats["Frazier"]["HRs"]
    murphy_hrs = stats["Murphy"]["HRs"]
    suarez_hrs = stats["Suarez"]["HRs"]
    over_unders["OldHomers"]["Current"] = haniger_hrs + frazier_hrs + murphy_hrs + suarez_hrs
    over_unders["OldHomers"]["Projected"] = 162 / (wins + losses) * (
                haniger_hrs + frazier_hrs + murphy_hrs + suarez_hrs)

    rodriguez_hrs = stats["Rodriguez"]["HRs"]
    kelenic_hrs = stats["Kelenic"]["HRs"]
    over_unders["YoungHomers"]["Current"] = rodriguez_hrs + kelenic_hrs
    over_unders["YoungHomers"]["Projected"] = 162 / (wins + losses) * (
                rodriguez_hrs + kelenic_hrs)

    row_template = "<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{num1:.{places1}f}</td><td>{num2:.{places2}f}</td>"
    rows = []
    for over_under in over_unders:
        item = over_unders[over_under]

        rounding = item["Rounding"]
        row = row_template
        row = row.format(item["Title"], item["Value"],
                         maybe_bold("Over", item["Over"], item["Projected"], item["Value"]),
                         maybe_bold("Under", item["Under"], item["Projected"], item["Value"]),
                         num1=item["Current"], places1=rounding[0], num2=item["Projected"], places2=rounding[1])
        rows.append(row)

    return over_unders, "<tr>" + "</tr>\r\n<tr>".join(rows) + "</tr>"


def get_other_table(stats):
    others = {
        "BestTeam": {
            "Title": "Team WAR"
        },
        "BestPlayer": {
            "Title": "Player WAR"
        }
    }

    # Team WAR
    hans_team_war = stats["Mariners"]["Hans"]
    gregory_team_war = stats["Mariners"]["Gregory"]
    if gregory_team_war > hans_team_war:
        others["BestTeam"]["Best"] = "Team Gregory"
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(gregory_team_war)
        others["BestTeam"]["Winner"] = "Gregory"
    elif hans_team_war > gregory_team_war:
        others["BestTeam"]["Best"] = "Team Hans"
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(hans_team_war)
        others["BestTeam"]["Winner"] = "Hans"
    else:
        others["BestTeam"]["Best"] = "Team Hans, Team Gregory"
        others["BestTeam"]["Relevant"] = "{:.1f} WAR".format(hans_team_war)
        others["BestTeam"]["Winner"] = "Hans, Gregory"


    # Best Player(s)
    global_high_war = -10
    best_players = []
    winners = []
    for team in teams:
        for player in teams[team]:
            if stats[player[1]]["WAR"] > global_high_war:
                best_players = [player[2]]
                global_high_war = stats[player[1]]["WAR"]
                winners = [team]
            elif stats[player[1]]["WAR"] == global_high_war:
                best_players.append(player[2])
                if team not in winners:
                    winners.append(team)

    others["BestPlayer"]["Best"] = ", ".join(best_players)
    others["BestPlayer"]["Relevant"] = "{:.1f} WAR".format(global_high_war)
    others["BestPlayer"]["Winner"] = ", ".join(winners)

    row_template = "<td>{}</td><td>{}</td><td>{}</td><td class='bold'>{}</td>"
    rows = []
    for other in others:
        item = others[other]
        row = row_template
        row = row.format(item["Title"], item["Best"], item["Relevant"], item["Winner"])
        rows.append(row)

    return others, "<tr>" + "</tr>\r\n<tr>".join(rows) + "</tr>"


def calculate_scores(over_unders, others):
    hans = 0
    gregory = 0
    for item in over_unders:
        over = over_unders[item]["Projected"] > over_unders[item]["Value"]
        if over and over_unders[item]["Over"] == "Hans":
            hans += 1
        elif not over and over_unders[item]["Under"] == "Hans":
            hans += 1
        else:
            gregory += 1

    for item in others:
        if "Hans" in others[item]["Winner"] and "Gregory" in others[item]["Winner"]:
            hans += .5
            gregory += .5
        elif "Hans" in others[item]["Winner"]:
            hans += 1
        elif "Gregory" in others[item]["Winner"]:
            gregory += 1

    return hans, gregory


def save_stats(stats):
    gp = stats["Mariners"]["Wins"] + stats["Mariners"]["Losses"]
    daily_data_file_name = DATA_FILE_PATH.format(str(gp))
    stats_json = json.dumps(stats)
    stats_file = open(daily_data_file_name, "w")
    stats_file.write(stats_json)
    stats_file.close()


def get_previous_data(gp):
    attempt = 0
    stats = None
    while attempt < 163 and stats is None:
        attempt += 1
        previous_data_file_name = DATA_FILE_PATH.format(str(gp - attempt))
        print(previous_data_file_name)
        if os.path.exists(previous_data_file_name):
            with open(previous_data_file_name) as previous_data_file:
                stats = json.load(previous_data_file)
                return gp - attempt, stats


def save_html(site_html):
    index_html_file = open("white_board.html", "w")
    index_html_file.write(site_html)
    index_html_file.close()


def upload_site():
    with open("/home/pi/Project/PythonProjects/Baseball2022/ftp_creds.json") as ftp_creds_file:
        ftp_creds = json.load(ftp_creds_file)
        index_html_file = open("white_board.html", "rb")
        ftp = FTP(ftp_creds["FTP_Site"])
        try:
            ftp.login(ftp_creds["FTP_UserName"], ftp_creds["FTP_Password"])
            ftp.cwd("cakewood.net")
            ftp.cwd("2022BaseballOverUnder")
            ftp.sendcmd('TYPE A')
            ftp.storlines('STOR white_board.html', index_html_file)
        except Exception as e:
            print(e)
        finally:
            ftp.close()

        index_html_file.close()


def main():
    # get today's stats
    new_stats = get_stat_dict()

    # load previous stats from file
    games_played = new_stats["Mariners"]["Wins"] + new_stats["Mariners"]["Losses"]
    print(games_played)
    previous_games_played, old_stats = get_previous_data(games_played)

    html_base = None
    with open('white_board.template', "r") as text_file:
        html_base = text_file.readlines()
    html_base = ''.join(html_base)
    html_text = html_base

    # set last updated and other header stuff
    html_text = html_text.replace("<LastUpdated/>", datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"))
    html_text = html_text.replace("<GamesPlayed/>", str(games_played))
    html_text = html_text.replace("<PreviousGamesPlayed/>", str(previous_games_played))

    # set team tables
    team_tables = get_team_tables(new_stats, old_stats)
    html_text = html_text.replace("<TeamTables/>", team_tables)

    # win table
    record_table_html = get_projected_record_table(new_stats)
    html_text = html_text.replace("<RecordTable/>", record_table_html)

    # over/under table
    over_unders, row_html = get_over_under_table(new_stats)
    html_text = html_text.replace("<OverUnderRows/>", row_html)

    # other table
    others, row_html = get_other_table(new_stats)
    html_text = html_text.replace("<OtherRows/>", row_html)

    # put in totals
    hans, gregory = calculate_scores(over_unders, others)
    html_text = html_text.replace("<Hans/>", str(hans))
    html_text = html_text.replace("<Gregory/>", str(gregory))

    save_html(html_text)
    upload_site()

    # saving these at the end because they get updated a couple of times throughout the process
    save_stats(new_stats)


if __name__ == "__main__":
    while True:
        print("Running: {}".format(datetime.utcnow()))
        main()
        sleep_time = random.randint(180, 240)
        print("Sleeping for {} minutes.".format(sleep_time))
        time.sleep(60 * sleep_time)
