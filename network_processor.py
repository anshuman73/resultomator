"""
Copyright 2017, Anshuman Agarwal (Anshuman73)
Licensed under CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/)
"""

import grequests
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import sqlite3
import os


def parser(html):
    html = ''.join(html.split('\n')[100:])
    data = dict()
    marks_table_index = list()
    marks = list()
    soup = BeautifulSoup(html, 'html.parser')
    parsed_tables = soup.findAll('table')[:2]
    basic_data_table = parsed_tables[0]
    basic_data_tr = basic_data_table.findAll('tr')
    for rows in basic_data_tr:
        columns = rows.findAll('td')
        data[''.join(columns[0].findAll(text=True)).strip()] = ''.join(columns[1].findAll(text=True)).strip()

    result_data_table = parsed_tables[1]
    result_data_tr = result_data_table.findAll('tr')
    for codes in result_data_tr[0].findAll('td'):
        marks_table_index.append(''.join(codes.findAll(text=True)).strip())

    marks_table_subjects = result_data_tr[1:-1]
    for subject_tr in marks_table_subjects:
        if len(subject_tr.findAll('td')) > 1:
            subject_marks = dict()
            for index, sub_details in enumerate(subject_tr.findAll('td')):
                subject_marks[marks_table_index[index]] = ''.join(sub_details.findAll(text=True)).strip()
            marks.append(subject_marks)

    raw_result = ''.join(result_data_tr[-1].findAll('td')[1].findAll(text=True)).strip()
    result = raw_result[raw_result.find('Result :') + len('Result :') + 1: raw_result.rfind(':')].strip()

    data['marks'] = marks
    data['final_result'] = result
    return data


def process_range(string_inp):
    final_range = list()
    string_inp = string_inp.split(',')
    for inp in string_inp:
        if '-' in inp:
            inp = inp.split('-')
            try:
                final_range.extend(range(int(inp[0].strip()), int(inp[1].strip()) + 1))
            except ValueError:
                print('Invalid input {} ignored'.format(str(inp)))
        else:
            try:
                final_range.append(int(inp.strip()))
            except ValueError:
                print('Invalid input {} ignored'.format(str(inp)))
    final_range.sort()
    return final_range


def process(school_code, roll_no_range, centre_no, net_choice):
    if not os.path.exists('./webpages'):
        os.mkdir('./webpages')
    database_conn = sqlite3.connect('raw_data.sqlite')
    cursor = database_conn.cursor()
    cursor.executescript('''
                        DROP TABLE IF EXISTS Records;
                        DROP TABLE IF EXISTS Marks;
                        CREATE TABLE IF NOT EXISTS Records (
                            Roll_Number        INTEGER PRIMARY KEY,
                            Name               TEXT,
                            Father_Name        TEXT,
                            Mother_Name        TEXT,
                            Final_Result       TEXT,
                            Number_of_subjects INTEGER
                            );
                        CREATE TABLE IF NOT EXISTS Marks (
                            Roll_Number INTEGER,
                            Subject_Code    TEXT,
                            Subject_Name    TEXT,
                            Theory_Marks    INTEGER,
                            Practical_Marks INTEGER,
                            Total_Marks     INTEGER,
                            Grade           TEXT
                            )
                        ''')

    roll_no_range = process_range(roll_no_range)
    if net_choice == 'y':
        net_choice = True
    elif net_choice == 'n':
        net_choice = False
    else:
        print('\nIncorrect Network mode chosen, defaulting to non-async\n')
        net_choice = False
    count = 0
    headers = {'Referer': 'http://cbseresults.nic.in/class12npy/class12th17reval.htm',
               'Upgrade-Insecure-grequests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                             ' Chrome/58.0.3029.110 Safari/537.36'}
    payloads = [{'regno': roll_no, 'sch': school_code, 'cno': centre_no, 'B2': 'Submit'} for roll_no in roll_no_range]
    base_url = 'http://cbseresults.nic.in/class12npy/class12th17reval.asp'
    print('Retrieving data for {} students, may take a few seconds depending on the network\n'.format(len(payloads)))
    if net_choice:
        responses = (grequests.post(base_url, headers=headers, data=load) for load in payloads)
        page_sources = grequests.map(responses)
    else:
        page_sources = list()
        for load in payloads:
            roll_no = load['regno']
            try:
                page_sources.append(requests.post(base_url, headers=headers, data=load))
            except ConnectionError:
                page_sources.append(None)
            except Exception as error:
                page_sources.append(None)
                print('AAAAHHHHHH. Roll No. {} threw an unknown, unexpected error, call the developer.'.format(roll_no))
                print('Report this error to him: {}'.format(error))

    print('Retrieved data for {} records out of {} records asked for.\n'.format(len(page_sources), len(payloads)))
    for page_source in page_sources:
        roll_no = roll_no_range[page_sources.index(page_source)]
        try:
            if page_source and page_source.status_code == 200:
                data = parser(page_source.text)
                cursor.execute('INSERT INTO Records (Roll_Number, Name, Father_Name, Mother_Name, Final_Result, '
                               'Number_of_subjects) VALUES (?, ?, ?, ?, ?, ?)',
                               (data['Roll No:'], data['Candidate Name:'], data['Father\'s Name:'],
                                data['Mother\'s Name:'], data['final_result'], len(data['marks']), ))
                for subject in data['marks']:
                    cursor.execute('INSERT INTO Marks (Roll_Number, Subject_Code, Subject_Name, Theory_Marks,'
                                   'Practical_Marks, Total_Marks, Grade) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                   (data['Roll No:'], subject['SUB CODE'], subject['SUB NAME'], subject['THEORY'],
                                    subject['PRACTICAL'], subject['MARKS'], subject['GRADE'], ))
                with open('./webpages/{}-{}.html'.format(data['Roll No:'], data['Candidate Name:']), 'w') as html_page:
                    html_page.write(page_source.text)
                count += 1
            else:
                print('Failed to retrieve data for Roll No. {}'.format(roll_no))

        except IndexError:
            print('Result not found for this Roll Number-School Code combination: {}-{}'.format(roll_no, school_code))
        except Exception as error:
            print('AAAAHHHHHH. Roll No. {} threw an unknown, unexpected error, call the developer.'.format(roll_no))
            print('Report this error to him: {}'.format(error))

    database_conn.commit()
    database_conn.close()
    print('{} valid records downloaded and saved'.format(count))


if __name__ == '__main__':  # Allows to use it as standalone, for demonstration purposes

    schcode = input('Enter the School Code: ')
    roll_range = input('Enter range of roll numbers. Use "-" for entering ranges and use "," to separate inputs: ')
    cen_no = input('Enter the common centre number: ')
    net_ch = input('Go async mode for network requests ? (Y/N): ').strip().lower()

    process(schcode, roll_range, cen_no, net_ch)
