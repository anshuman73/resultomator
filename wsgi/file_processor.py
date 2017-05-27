"""
Copyright 2017, Anshuman Agarwal (Anshuman73)
Licensed under CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/)
"""

import sqlite3
import os


def get_subject_names():
    # Generate a dictionary to use from a text file which has codes vs subject for all CBSE subjects.
    # Obtained from http://cbseacademic.in/web_material/Curriculum/SrSecondary/2014_XII_Subject_Code_List.pdf
    names = dict()
    subject_codes_file = open('subject_codes.txt')
    sub_code_data = subject_codes_file.readlines()
    for subject in sub_code_data:
        subject = subject.split(maxsplit=2)
        names[subject[1].strip()] = subject[2].strip()
    subject_codes_file.close()
    return names


def clean_data(text_data):
    clean_txt_data = list()
    for line in text_data.split('\n'):
        try:
            int(line.split(' ')[0])
            clean_txt_data.append(line.strip())
        except ValueError:
            pass
    return clean_txt_data


def extract_metadata(file_data):
    school_data = file_data[file_data.find(':', file_data.find('\nSCHOOL')) + 1:
                            file_data.find('\n', file_data.find(':', file_data.find('\nSCHOOL')))].split(maxsplit=1)
    school_code = school_data[0].strip()
    school_name = school_data[1].strip().title()

    index_start = file_data.find('SUB', file_data.find('CANDIDATE NAME'))
    index_end = file_data.find('SUB', index_start + 1)
    subject_split_index = index_end - index_start

    return school_name, school_code, subject_split_index


def split_result_data(result_data, subject_split_index=15):
    return [result_data[i:i + subject_split_index].strip() for i in range(0, len(result_data), subject_split_index)]


def process(file_address):
    database_conn = sqlite3.connect(os.environ['OPENSHIFT_DATA_DIR'] + 'raw_data.sqlite')
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

    subject_names = get_subject_names()

    txt_file = open(file_address)
    txt_file_data = txt_file.read()
    school_name, school_code, subject_split_index = extract_metadata(txt_file_data)
    data = clean_data(txt_file_data)
    print('Data found for {} (School Code - {})\n'.format(school_name, school_code))
    print('Found data for {} students\n'.format(len(data)))
    for line in data:
        line = line.split('    ', maxsplit=1)
        student_data = line[0].strip().split(' ', maxsplit=1)
        results_data = ''.join(line[1:]).strip().split('     ')
        final_result = results_data[1][-4:]
        result_data = split_result_data(''.join(results_data[:-1]), subject_split_index)
        roll_no = student_data[0]
        student_name = student_data[1]
        subject_count = 0
        for subject_data in result_data:
            subject_data = subject_data.split()
            if len(subject_data):
                subject_count += 1
                subject_code = subject_data[0]
                total_marks = grade = ''  # Needed as student who were absent may not have any data.
                try:
                    total_marks = subject_data[1]
                    grade = subject_data[2]
                except IndexError:
                    pass
                cursor.execute('INSERT INTO Marks (Roll_Number, Subject_Code, Subject_Name, Theory_Marks,'
                               'Practical_Marks, Total_Marks, Grade) VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (roll_no, subject_code, subject_names[subject_code], '', '', total_marks, grade,))

        cursor.execute('INSERT INTO Records (Roll_Number, Name, Father_Name, Mother_Name, Final_Result, '
                       'Number_of_subjects) VALUES (?, ?, ?, ?, ?, ?)',
                       (roll_no, student_name, '', '', final_result, subject_count,))

    txt_file.close()
    database_conn.commit()
    database_conn.close()
    print('Saved data for {} students\n'.format(len(data)))

if __name__ == '__main__':
    process(str(input('Enter the location of the text file received in the E-Mail: ')))
