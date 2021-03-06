"""
Copyright 2017, Anshuman Agarwal (Anshuman73)
Licensed under CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/)
"""

import sqlite3
import json


def clean():
    raw_db_conn = sqlite3.connect('raw_data.sqlite')
    raw_db_cursor = raw_db_conn.cursor()
    clean_db_conn = sqlite3.connect('clean_data.sqlite')
    clean_db_cursor = clean_db_conn.cursor()
    # Delete existing tables if a db exists already
    clean_db_cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    existing_tables = clean_db_cursor.fetchall()
    for table in existing_tables:
        clean_db_cursor.execute('DROP TABLE {}'.format(str(table[0])))
    clean_db_cursor.executescript('''
                                  CREATE TABLE IF NOT EXISTS Subjects (
                                      Subject_Code TEXT PRIMARY KEY,
                                      Subject_Name TEXT
                                      );
                                  CREATE TABLE IF NOT EXISTS Students (
                                      Roll_Number        INTEGER PRIMARY KEY,
                                      Name               TEXT,
                                      Father_Name        TEXT,
                                      Mother_Name        TEXT,
                                      Number_of_subjects INTEGER,
                                      Subjects           TEXT,
                                      Final_Result       TEXT
                                      )
                                  ''')

    # Fill data in Subjects table.
    # Gets unique subject code values and puts them in table with the name
    print('Normalizing Subject data\n')
    raw_db_cursor.execute('SELECT DISTINCT Subject_Code, Subject_Name FROM Marks ORDER BY Subject_Code')
    subject_code_combos = raw_db_cursor.fetchall()
    for code, name in subject_code_combos:
        clean_db_cursor.execute('INSERT INTO Subjects (Subject_Code, Subject_Name) VALUES (?, ?)',
                                (str(code), name.title(), ))

    # Now we take all the subject codes from the newly formed table and create tables for each subject code
    clean_db_cursor.execute('SELECT Subject_Code FROM Subjects;')
    all_subs = clean_db_cursor.fetchall()
    for code in all_subs:
        # Probably a worry for injection, remove if going web app ish
        # Underscore before sub_code as initial char numeric is not supported by sqlite
        clean_db_cursor.execute('''
                                CREATE TABLE IF NOT EXISTS _{} (
                                    Roll_Number     INTEGER PRIMARY KEY,
                                    Theory_Marks    INTEGER,
                                    Practical_Marks INTEGER,
                                    Total_Marks     INTEGER,
                                    Grade           TEXT
                                    )
                                '''.format(str(code[0])))

    # Fill data in the Students Table
    # Gets all subjects from `Marks` table and sorts into the individual subjects tables.
    # Also generates json text dump for all subjects taken by the student
    print('Normalizing student records\n')
    raw_db_cursor.execute('SELECT Roll_Number, Name, Father_Name, Mother_Name, Final_Result, Number_of_subjects '
                          'FROM Records ORDER BY Roll_Number;')
    all_students = raw_db_cursor.fetchall()
    for student_details in all_students:
        raw_db_cursor.execute('SELECT Subject_Code, Theory_Marks, Practical_Marks, Total_Marks, Grade FROM Marks '
                              'WHERE Roll_Number=? ORDER BY Subject_Code;', (str(student_details[0]), ))
        student_subject_details = raw_db_cursor.fetchall()
        student_subjects = dict()
        # Convert tuple to dict with list values for easier data access.
        for sub, *marks in student_subject_details:
            student_subjects[sub] = marks
        all_sub_codes = json.dumps([sub_code for sub_code, marks in student_subjects.items()])
        # Insert clean student data
        clean_db_cursor.execute('INSERT INTO Students (Roll_Number, Name, Father_Name, Mother_Name, Number_of_Subjects,'
                                'Subjects, Final_Result) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                (str(student_details[0]), student_details[1].title(), student_details[2].title(),
                                 student_details[3].title(), str(student_details[5]), all_sub_codes,
                                 str(student_details[4]), ))
        # Insert cleaned subject data of each student in respective subject tables
        for sub_code, marks in student_subjects.items():
            clean_db_cursor.execute('INSERT INTO _{} (Roll_Number, Theory_Marks, Practical_Marks, Total_Marks, Grade) '
                                    'VALUES (?, ?, ?, ?, ?)'.format(sub_code), (str(student_details[0]), marks[0],
                                                                                marks[1], marks[2], marks[3], ))

    # Save and close all stuff, we're done.
    raw_db_conn.commit()
    raw_db_conn.close()
    clean_db_conn.commit()
    clean_db_conn.close()

if __name__ == '__main__':
    clean()
