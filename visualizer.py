"""
Copyright 2017, Anshuman Agarwal (Anshuman73)
Licensed under CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/)
"""

import xlsxwriter
import sqlite3
import json

'''
This module does more than just data viz.
The first step is to create excel files and dump all the data in different worksheets.
The next step is to create data viz, using D3 or something similar (numpy, scipy ?) to create HTML files(or PDFs/PNGs ?)
'''


def excelify():
    db_conn = sqlite3.connect('clean_data.sqlite')
    db_cursor = db_conn.cursor()

    main_workbook = xlsxwriter.Workbook('All CBSE 12th results.xlsx')
    main_worksheet = main_workbook.add_worksheet("Results")
    subject_workbook = xlsxwriter.Workbook('CBSE 12th Subject-wise results.xlsx')

    main_heading_format = main_workbook.add_format({'bold': True, 'align': 'center'})
    main_left_align_format = main_workbook.add_format({'align': 'left'})
    sub_heading_format = subject_workbook.add_format({'bold': True, 'align': 'center'})
    sub_left_align_format = subject_workbook.add_format({'align': 'left'})

    db_cursor.execute('SELECT Roll_number, Name, Father_Name, Mother_name, Final_result, Subjects FROM Students '
                      'ORDER BY Roll_number ASC')
    student_data = db_cursor.fetchall()
    number_of_students = len(student_data)

    db_cursor.execute('SELECT Subject_Name, Subject_Code FROM Subjects ORDER BY Subject_Name')
    all_subjects = db_cursor.fetchall()
    number_of_subjects = len(all_subjects)

    main_worksheet.set_column(0, 0, 15)
    main_worksheet.set_column(1, 3, 30)
    main_worksheet.set_column(4, 2 * number_of_subjects + 5, 15)
    main_worksheet.set_row(0, 20, main_heading_format)
    main_worksheet.set_row(1, 20, main_heading_format)

    main_worksheet.write(0, 0, 'Roll Number')
    main_worksheet.write(0, 1, 'Name')
    main_worksheet.write(0, 2, 'Father\'s Name')
    main_worksheet.write(0, 3, 'Mother\'s Name')
    main_worksheet.write(0, 4, 'Final Result')

    subject_data = dict()

    for subject, code in all_subjects:
        subject_index = all_subjects.index((subject, code))
        sub_worksheet = subject_workbook.add_worksheet(str(subject))
        sub_worksheet.set_column(0, 0, 15)
        sub_worksheet.set_column(1, 1, 30)
        sub_worksheet.set_column(2, 5, 15)
        sub_worksheet.set_row(0, 20, sub_heading_format)
        sub_worksheet.write(0, 0, 'Roll Number')
        sub_worksheet.write(0, 1, 'Name')
        sub_worksheet.write(0, 2, 'Theory Marks')
        sub_worksheet.write(0, 3, 'Practical Marks')
        sub_worksheet.write(0, 4, 'Total Marks')
        sub_worksheet.write(0, 5, 'Grade')

        main_worksheet.merge_range(0, subject_index * 2 + 6, 0, subject_index * 2 + 7, str(subject))
        main_worksheet.write(1, subject_index * 2 + 6, 'Marks')
        main_worksheet.write(1, subject_index * 2 + 7, 'Grade')

        subject_code_data = dict()
        subject_code_data['subject_name'] = str(subject)
        subject_students = dict()

        db_cursor.execute('SELECT sub.Roll_Number, stud.Name, sub.Theory_Marks, sub.Practical_Marks, sub.Total_Marks,'
                          'sub.Grade FROM _{} sub JOIN Students stud ON sub.Roll_Number = stud.Roll_Number '
                          'ORDER BY sub.Total_Marks DESC, sub.Grade ASC, stud.Name ASC'.format(code))
        students_details = db_cursor.fetchall()
        number_of_students = len(students_details)
        for row_num in range(number_of_students):
            sub_worksheet.set_row(row_num + 2, 18, sub_left_align_format)
            sub_worksheet.write_row(row_num + 2, 0, students_details[row_num])

            subject_student_rollno = dict()
            subject_student_rollno['marks'] = students_details[row_num][4]
            subject_student_rollno['grade'] = students_details[row_num][5]
            subject_students[students_details[row_num][0]] = subject_student_rollno

        subject_code_data['students'] = subject_students
        subject_data[code] = subject_code_data

    for student_index in range(number_of_students):
        main_worksheet.set_row(student_index + 3, 18, main_left_align_format)
        main_worksheet.write_row(student_index + 3, 0, student_data[student_index][:-1])
        for subject_code in json.loads(student_data[student_index][-1]):
            main_worksheet.write(student_index + 3,
                                 all_subjects.index((subject_data[subject_code]['subject_name'], subject_code)) * 2 + 6,
                                 subject_data[subject_code]['students'][student_data[student_index][0]]['marks'])
            main_worksheet.write(student_index + 3,
                                 all_subjects.index((subject_data[subject_code]['subject_name'], subject_code)) * 2 + 7,
                                 subject_data[subject_code]['students'][student_data[student_index][0]]['grade'])

    main_workbook.close()
    subject_workbook.close()
    db_conn.close()


if __name__ == '__main__':
    excelify()

# TODO: If a column is empty or has '---' , then skip the creation of the column. This can be done in the cleaner module
# and then the excel columns can be generated on basis of a db query of columns in each subject table
