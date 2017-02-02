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

import xlsxwriter
import sqlite3

'''
This module does more than just data viz.
The first step is to create excel files and dump all the data in different worksheets.
The next step is to create data viz, using D3 or something similar (numpy, scipy ?) to create HTML files (or PDFs ?)
'''


def excelify():
    db_conn = sqlite3.connect('clean_data.sqlite')
    db_cursor = db_conn.cursor()

    main_workbook = xlsxwriter.Workbook('CBSE 12th results.xlsx')
    heading_format = main_workbook.add_format({'bold': True, 'align': 'center'})
    left_align_format = main_workbook.add_format({'align': 'left'})

    db_cursor.execute('SELECT Subject_Name, Subject_Code FROM Subjects ORDER BY Subject_Name')
    all_subjects = db_cursor.fetchall()
    for subject, code in all_subjects:
        sub_worksheet = main_workbook.add_worksheet(str(subject))
        sub_worksheet.set_column(0, 0, 15)
        sub_worksheet.set_column(1, 1, 30)
        sub_worksheet.set_column(2, 5, 15)
        sub_worksheet.set_row(0, 20, heading_format)
        sub_worksheet.write(0, 0, 'Roll Number')
        sub_worksheet.write(0, 1, 'Name')
        sub_worksheet.write(0, 2, 'Theory Marks')
        sub_worksheet.write(0, 3, 'Practical Marks')
        sub_worksheet.write(0, 4, 'Total Marks')
        sub_worksheet.write(0, 5, 'Grade')
        db_cursor.execute('SELECT sub.Roll_Number, stud.Name, sub.Theory_Marks, sub.Practical_Marks, sub.Total_Marks,'
                          'sub.Grade FROM _{} sub JOIN Students stud ON sub.Roll_Number = stud.Roll_Number '
                          'ORDER BY sub.Total_Marks DESC, stud.Name ASC'.format(code))
        students_details = db_cursor.fetchall()
        number_of_students = len(students_details)
        for row_num in range(2, number_of_students + 2):
            sub_worksheet.set_row(row_num, 18, left_align_format)
            sub_worksheet.write_row(row_num, 0, students_details[row_num - 2])

    main_workbook.close()

if __name__ == '__main__':
    excelify()

# TODO: If a column is empty or has '---' , then skip the creation of the column. This can be done in the cleaner module
# and then the excel columns can be generated on basis of a db query of columns in each subject table
