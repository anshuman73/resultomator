"""
Copyright 2017, Anshuman Agarwal (Anshuman73)
Licensed under CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/)
"""

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


# Generate a dictionary to use from a text file which has codes vs subject for all CBSE subjects.
# Obtained from http://cbseacademic.in/web_material/Curriculum/SrSecondary/2014_XII_Subject_Code_List.pdf
subject_names = dict()
sub_code_data = open('subject_codes.txt').readlines()
for subject in sub_code_data:
    subject = subject.split(maxsplit=2)
    subject_names[subject[1].strip()] = subject[2].strip()


def clean_data(text_data):
    clean_txt_data = list()
    for line in text_data:
        try:
            int(line.split(' ')[0])
            clean_txt_data.append(line.strip())
        except ValueError:
            pass
    return clean_txt_data


def split_result_data(result_data):
    return [result_data[i:i+13].strip() for i in range(0, len(result_data), 13)]


def process():
    txt_file_data = open('results.txt').readlines()
    data = clean_data(txt_file_data)
    for line in data:
        line = line.split('    ', maxsplit=1)
        student_data = line[0].strip().split(' ', maxsplit=1)
        result_data = split_result_data(''.join(line[1:]).strip())
        roll_no = student_data[0]
        student_name = student_data[1]
        final_result = result_data.pop()[-4:]
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

    database_conn.commit()
    database_conn.close()


if __name__ == '__main__':
    process()
