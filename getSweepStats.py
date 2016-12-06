#!/usr/bin/env python

"""

Leverage some good Euro2016 data to keep track of some stupid sweepstakes.
A script intended to run periodically in cron to keep track of a few sweepstakes, that would otherwise be to boring
to check manually.
Scrape a variety of sites to gather match stats, work out who's team is currently winning, output it all on
a Google Document to keep everyone updated.

"""

import bs4
import logging
import json
import re
import os
import requests
import argparse
from logging import handlers

# generic logging

formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('Sweepstaker')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


def get_result_data(sweepstake):
    """
    Scrape our data and make some Beautiful soups.
    Pull data from soups, work out winners/placements, build a results array with text to send to the Google APP
    :return: results
    """
    results = []

    # Wikipedia page sections
    # Sometimes these change so fetch the correct index each time

    sectionUrl = 'https://en.wikipedia.org/w/api.php?action=parse&page=UEFA_Euro_2016_statistics&prop=sections' \
                 '&sectiontitle=Scoring&format=json'
    scoring_index = ''
    sanctions_index = ''

    try:
        section_html = requests.get(sectionUrl)
    except IOError as e:
        logger.error(e)

    try:
        section_json = json.loads(section_html.text)
    except (ValueError, KeyError, TypeError) as e:
        logger.error(e)

    for section in section_json['parse']['sections']:
        if section['line'] == 'Scoring':
            scoring_index = section['index']
        if section['line'] == 'By team':
            sanctions_index = section['index']

    # URLS to scrape data from
    # Wikipedia API used to get the data in JSON

    scoringUrl = 'http://en.wikipedia.org/w/api.php?action=parse&page=UEFA_Euro_2016_statistics&prop=text' \
                 '&section=' + scoring_index + '&format=json&disablelimitreport=true&disableeditsection=true'
    goldenBootUrl = 'http://www.uefa.com/uefaeuro/golden-boot/index.html'
    disciplineUrl = 'http://en.wikipedia.org/w/api.php?action=parse&page=UEFA_Euro_2016_statistics&prop=text' \
                    '&section=' + sanctions_index + '&format=json&disablelimitreport=true&disableeditsection=true'

    # Make some soup

    try:
        scoring_html = requests.get(scoringUrl)
        golden_html = requests.get(goldenBootUrl)
        discipline_html = requests.get(disciplineUrl)
    except IOError as e:
        logger.error(e)

    try:
        scoring_json = json.loads(scoring_html.text)
        discipline_json = json.loads(discipline_html.text)
    except (ValueError, KeyError, TypeError) as e:
        logger.error(e)

    try:
        scoring = bs4.BeautifulSoup(scoring_json['parse']['text']['*'], "lxml")
        discipline = bs4.BeautifulSoup(discipline_json['parse']['text']['*'], "lxml")
        golden = bs4.BeautifulSoup(golden_html.text, "lxml")
    except:
        logger.info('BS/lxml parsing error')

    ### Fastest goal scored in a match from kickoff
    # Output the time, player, game and winner

    fastest_goal_stats = scoring.find('dt', string="Timing").parent.find_next('ul')\
        .find(string=re.compile("Fastest goal in a match from kickoff")).parent
    fastest_goal_time = {"fastest_goal_time": fastest_goal_stats.find('b').string}
    fastest_goal = fastest_goal_stats.find_all('a')

    fastest_goal_results = []
    fastest_goal_entry = {}
    fastest_goal_stat_counter = 0
    for pos, i in enumerate(fastest_goal, 1):
        if fastest_goal_stat_counter == 1:
            fastest_goal_entry['player'] = i.string
        if fastest_goal_stat_counter == 2:
            fastest_goal_entry['for_team'] = i.string
            fastest_goal_entry['owner'] = sweepstake[i.string]
        if fastest_goal_stat_counter == 3:
            fastest_goal_entry['against_team'] = i.string
            fastest_goal_results.append(fastest_goal_entry.copy())
        fastest_goal_stat_counter += 1
        if pos % 4 == 0:
            fastest_goal_stat_counter = 0
    
    results.append(fastest_goal_time)
    results.append(fastest_goal_results)
    

    # Console output
    #
    # print "*** Fastest goal ***\n"
    # print "Time: " + fastest_goal_time['fastest_goal_time']
    # for data in fastest_goal_results:
    #    print "Player: " + data['player'] + "\n"\
    #        'Team: ' + data['for_team'] + "\n"\
    #        'Against: ' + data['against_team'] + "\n"\
    #        'Winner: ' + data['owner'] + \
    #        "\n"

    ### Worst drubbing (biggest margin of loss)
    # Output goal difference, each team plus their score, and winner(losing team owner wins)

    biggest_margin_stats = scoring.find('dt', string="Teams").parent.find_next('ul')\
        .find(string=re.compile("Biggest margin of victory")).parent
    biggest_margin_amount = {"biggest_margin_amount": biggest_margin_stats.find('b').string}
    biggest_margin_games = biggest_margin_stats.find_all('a')
    
    biggest_margin_results = []
    biggest_margin_entry = {}
    biggest_margin_counter = 1
    
    for pos, i in enumerate(biggest_margin_games, 1):
        if biggest_margin_counter == 1:
            biggest_margin_entry['for_team'] = i.string
        if biggest_margin_counter == 2:
            score1 = int(i.string.split(u'\u2013')[0])
            score2 = int(i.string.split(u'\u2013')[1])
            total = score1 + score2
            biggest_margin_entry['for_team_score'] = score1
            biggest_margin_entry['total_goals'] = (score1 + score2)
            biggest_margin_entry['against_team_score'] = score2
        if biggest_margin_counter == 3:
            biggest_margin_entry['against_team'] = i.string
            if biggest_margin_entry['for_team_score'] < biggest_margin_entry['against_team_score']:
                biggest_margin_entry['owner'] = sweepstake[biggest_margin_entry['for_team']]
            else:
                biggest_margin_entry['owner'] = sweepstake[i.string]
            biggest_margin_results.append(biggest_margin_entry.copy())
            biggest_margin_entry.clear()
        biggest_margin_counter += 1
        if pos % 3 == 0:
            biggest_margin_counter = 1
    
    # Sort results - max total goals wins where margin is the same for more than one game
    biggest_margin_results = sorted(biggest_margin_results, key=lambda max: max['total_goals'], reverse=True)
    
    biggest_margin_winners = []
    current_max_goals = 0
    for match in biggest_margin_results:
        total = match['total_goals']
        if total >= current_max_goals:
            current_max_goals = total
            biggest_margin_winners.append(match)
    
    results.append(biggest_margin_amount)
    results.append(biggest_margin_winners)
   
    # Console output
    # 
    # print "*** Worst drubbing ***\n"
    # print "Margin: " + biggest_margin_amount['biggest_margin_amount'] + "\n"
    # for data in biggest_margin_results:
    #     print data['for_team'] + " " +\
    #     str(data['for_team_score']) + ' - ' + \
    #     str(data['against_team_score']) + " " +\
    #     data['against_team'] + "\n" +\
    #     "Winner: " + data['owner'] + "\n"

    ### Golden boot
    # Output the top 3 golden boots: player, team, goals, winner

    golden_boot_stats = {}
    
    golden_boot_stats['golden_player_1'] = golden.find('div', class_="podium-1")\
        .find('div', class_="podium--player-name").find('a').string.strip()
    golden_boot_stats['golden_team_1'] = golden.find('div', class_="podium-1")\
        .find('span', class_="team-name_name").string.strip()
    golden_boot_stats['golden_goals_1'] = golden.find('div', class_="podium-1")\
        .find('div', class_="podium--content").find('dd', class_="podium--content-data").string
    golden_boot_stats['golden_owner_1'] = sweepstake[golden_boot_stats['golden_team_1']] 
    
    golden_boot_stats['golden_player_2'] = golden.find('div', class_="podium-2")\
        .find('div', class_="podium--player-name").find('a').string.strip()
    golden_boot_stats['golden_team_2'] = golden.find('div', class_="podium-2")\
        .find('span', class_="team-name_name").string.strip()
    golden_boot_stats['golden_goals_2'] = golden.find('div', class_="podium-2")\
        .find('div', class_="podium--content").find('dd', class_="podium--content-data").string
    golden_boot_stats['golden_owner_2'] = sweepstake[golden_boot_stats['golden_team_2']] 

    golden_boot_stats['golden_player_3'] = golden.find('div', class_="podium-3")\
        .find('div', class_="podium--player-name").find('a').string.strip()
    golden_boot_stats['golden_team_3'] = golden.find('div', class_="podium-3")\
        .find('span', class_="team-name_name").string.strip()
    golden_boot_stats['golden_goals_3'] = golden.find('div', class_="podium-3")\
        .find('div', class_="podium--content").find('dd', class_="podium--content-data").string
    golden_boot_stats['golden_owner_3'] = sweepstake[golden_boot_stats['golden_team_3']] 

    results.append(golden_boot_stats)

    # Console output
    #
    # print "*** Golden boot ***\n\n" + \
    # "Goals: " + golden_boot_stats['golden_goals'] + "\n" \
    # "Player: " + golden_boot_stats['golden_player'] + "\n" \
    # "Team: " + golden_boot_stats['golden_team'] + "\n" \
    # "Winner: " + golden_boot_stats['golden_owner'] + "\n"

    ### Dirtiest Team
    # Output the top 3 dirtiest teams: team, red cards, yellow cards, score, winner
    
    dirtiest_team_results = {}
    dirtiest_team_list = []
    
    for i in range(1, 11):
        dirtiest_team_stats = discipline.find('table').find_all('tr')[i]
    
        dirtiest_team_results['dirtiest_team'] = dirtiest_team_stats.find('td').find('a').string 
        dirtiest_team_results['dirtiest_team_reds'] = dirtiest_team_stats.find_all('td')[1].string 
        dirtiest_team_results['dirtiest_team_yellows'] = dirtiest_team_stats.find_all('td')[2].string 
        dirtiest_team_results['dirtiest_team_score'] = (int(dirtiest_team_results['dirtiest_team_reds']) * 2) + \
            int(dirtiest_team_results['dirtiest_team_yellows'])
        dirtiest_team_results['dirtiest_team_owner'] = sweepstake[dirtiest_team_results['dirtiest_team']]
        dirtiest_team_list.append(dirtiest_team_results.copy())
        dirtiest_team_results.clear()
  
    dirtiest_team_list = sorted(dirtiest_team_list, key=lambda max: max['dirtiest_team_score'], reverse=True)

    results.append(dirtiest_team_list)

    # Console output
    #
    # print "*** Dirtiest Team ***\n\n" + \
    # "Team: " + dirtiest_team_results['dirtiest_team'] + "\n" \
    # "Red cards: " + dirtiest_team_results['dirtiest_team_reds'] + "\n" \
    # "Yellow cards: " + dirtiest_team_results['dirtiest_team_yellows'] + "\n" \
    # "Winner: " + dirtiest_team_results['dirtiest_team_owner'] + "\n"

    return results


def main():

    # Stakeholders
    sweepstake = {
        "Wales": "Pedro",
        "Portugal": "Pedro",
        "Northern Ireland": "Pedro",
        "Turkey": "Adam",
        "Czech Republic": "Adam",
        "Albania": "Adam",
        "Spain": "Clarkey",
        "Poland": "Clarkey",
        "Hungary": "Clarkey",
        "Romania": "Yozzer",
        "Russia": "Yozzer",
        "England": "Yozzer",
        "Italy": "Sisson",
        "Germany": "Sisson",
        "Switzerland": "Sisson",
        "Iceland": "Davo",
        "France": "Davo",
        "Sweden": "Davo",
        "Ukraine": "Paul",
        "Croatia": "Paul",
        "Republic of Ireland": "Paul",
        "Slovakia": "Fatboy",
        "Austria": "Fatboy",
        "Belgium": "Fatboy"
    }

    # args
    parser = argparse.ArgumentParser(
        description='Euro2016 Sweepstake tracker'
    )
    parser.add_argument("-dump", action='store_true', help="Dump JSON data and exit")
    parser.add_argument("-log", help="Path to log to")
    args = parser.parse_args()

    if args.log is not None:
        fh = logging.handlers.RotatingFileHandler(args.log, maxBytes=5000, backupCount=3)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    logger.debug("Running sweepstats")

    # Get data

    try:
        results_data = get_result_data(sweepstake)
    except:
        exit(1)

    payload = {'data': json.dumps(results_data)}

    if args.dump:
        print(payload)
    else:

        # Check google app url environment variable is set to something

        googleAppUrl = os.environ.get('GOOGLEAPPURL')

        if googleAppUrl is None:
            print("No Google App url set")
            raise SystemExit

        # Send the results data to our Google Scripts App to update/create the document

        try:
            requests.get(googleAppUrl, params=payload)
        except requests.exceptions.RequestException as err:
            logger.debug(err)

    exit(0)

if __name__ == '__main__':
    main()
