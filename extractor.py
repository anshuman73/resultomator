"""
Copyright 2017, Anshuman Agarwal (Anshuman73)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import grequests
import requests
from bs4 import BeautifulSoup
import sqlite3


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


def parser(html):
    html = ''.join(html.split('\n')[67:])
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
            subject_marks = {}
            for index, sub_details in enumerate(subject_tr.findAll('td')):
                subject_marks[marks_table_index[index]] = ''.join(sub_details.findAll(text=True)).strip()
            marks.append(subject_marks)

    raw_result = ''.join(result_data_tr[-1].findAll('td')[1].findAll(text=True)).strip()
    result = raw_result[raw_result.find('Result:') + len('Result:'): raw_result.rfind(':')].strip()

    data['marks'] = marks
    data['final_result'] = result
    return data


def extract(school_code, lower_limit, upper_limit, net_choice):
    if net_choice == 'y':
        net_choice = True
    elif net_choice == 'n':
        net_choice = False
    else:
        print('\nIncorrect Network mode chosen, defaulting to non-async\n')
        net_choice = False
    count = 0
    headers = {'Referer': 'http://cbseresults.nic.in/class12/cbse1216.htm', 'Upgrade-Insecure-grequests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/53.0.2785.116 Safari/537.36'}
    urls = ['http://cbseresults.nic.in/class12/cbse1216.asp?regno={}&schcode={}&B1=Submit'
            .format(roll_no, school_code) for roll_no in range(lower_limit, upper_limit + 1)]
    print('Retrieving data for {} students, may take a few seconds depending on the network\n'.format(len(urls)))
    if net_choice:
        responses = (grequests.get(u, headers=headers) for u in urls)
        page_sources = grequests.map(responses)
    else:
        page_sources = list()
        for url in urls:
            roll_no = url[url.find('=') + 1:url.find('&')]
            try:
                page_sources.append(requests.get(url, headers=headers))
            except requests.exceptions.ConnectionError:
                page_sources.append(None)
            except Exception as error:
                print('Some unknown, unexpected error has been thrown, call the developer. AAAAHHHHHH')
                print('Report this error to him: {}'.format(error))

    print('Retrieved data for {} records out of {} records asked for.\n'
          .format(len(page_sources), len(urls)))
    for page_source in page_sources:
        try:
            if page_source and page_source.status_code == 200:
                roll_no = page_source.url[page_source.url.find('=') + 1:page_source.url.find('&')]
                data = parser(page_source.text)
                cursor.execute('INSERT INTO Records (Roll_Number, Name, Father_Name, Mother_Name, Final_Result, '
                               'Number_of_subjects) VALUES (?, ?, ?, ?, ?, ?)',
                               (data['Roll No:'], data['Name:'], data['Father\'s Name:'], data['Mother\'s Name:'],
                                data['final_result'], len(data['marks']), ))
                for subject in data['marks']:
                    cursor.execute('INSERT INTO Marks (Roll_Number, Subject_Code, Subject_Name, Theory_Marks,'
                                   'Practical_Marks, Total_Marks, Grade) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                   (data['Roll No:'], subject['SUB CODE'], subject['SUB NAME'], subject['THEORY'],
                                    subject['PRACTICAL'], subject['MARKS'], subject['GRADE'], ))
                count += 1
            else:
                print('Failed to retrieve data for Roll No. {}'.format(roll_no))

        except IndexError:
            print('Result not found for this Roll Number-School Code combination: {}-{}'.format(roll_no, school_code))
        except Exception as error:
            print('Some unknown, unexpected error has been thrown, call the developer. AAAAHHHHHH')
            print('Report this error to him: {}'.format(error))

    database_conn.commit()
    database_conn.close()
    print('{} valid records downloaded and saved in the range {} to {} (both inclusive),'
          .format(count, lower_limit, upper_limit))


if __name__ == '__main__':  # Allows to use it as standalone, for demonstration purposes

    schcode = int(input('Enter the School Code: '))
    lwr = int(input('Enter the lower limit of the Roll Numbers: '))
    upr = int(input('Enter the upper limit of the Roll Numbers: '))
    net_ch = input('Go async mode for network requests ? (Y/N): ').strip().lower()

    extract(schcode, lwr, upr, net_ch)
