"""
Copyright 2017, Anshuman Agarwal (Anshuman73)
Licensed under CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/)
"""

import xlsxwriter
import sqlite3
import json
from xlsxwriter.utility import xl_range


def get_best(english_marks, student_marks):
    to_remove = list()
    for x in range(len(student_marks)):
        if type(student_marks[x]) != int:
            to_remove.append(x)
    to_remove.sort(reverse=True)  # Sorting required as the changing indexes don't mess up the process
    for x in to_remove:
        student_marks.pop(x)
    return (english_marks + sum(sorted(student_marks, reverse=True)[:4])) / 5


def excelify():
    db_conn = sqlite3.connect('clean_data.sqlite')
    db_cursor = db_conn.cursor()

    main_workbook = xlsxwriter.Workbook('All CBSE 12th results.xlsx')
    main_worksheet = main_workbook.add_worksheet("Results")
    subject_workbook = xlsxwriter.Workbook('CBSE 12th Subject-wise results.xlsx')

    main_heading_format = main_workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                                    'font_size': 13})
    main_left_align_format = main_workbook.add_format({'align': 'left', 'valign': 'vcenter'})
    sub_heading_format = subject_workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                                      'font_size': 13})
    sub_left_align_format = subject_workbook.add_format({'align': 'left', 'valign': 'vcenter'})
    sub_center_align_format = subject_workbook.add_format({'align': 'center', 'valign': 'vcenter'})
    possible_grades = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'E']

    db_cursor.execute('SELECT Roll_number, Name, Father_Name, Mother_name, Final_result, Subjects FROM Students '
                      'ORDER BY Roll_number ASC')
    student_data = db_cursor.fetchall()
    number_of_students = len(student_data)

    db_cursor.execute('SELECT Subject_Name, Subject_Code FROM Subjects ORDER BY Subject_Name')
    all_subjects = db_cursor.fetchall()
    number_of_subjects = len(all_subjects)

    main_worksheet.set_column(0, 0, 15)
    main_worksheet.set_column(1, 3, 30)
    main_worksheet.set_column(4, 2 * number_of_subjects + 7, 20)
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
        sub_worksheet.set_column(2, 5, 20)
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
            sub_worksheet.set_row(row_num + 2, 18)
            sub_worksheet.write_row(row_num + 2, 0, students_details[row_num][:2], sub_left_align_format)
            sub_worksheet.write_row(row_num + 2, 2, students_details[row_num][2:], sub_center_align_format)

            subject_student_rollno = dict()
            subject_student_rollno['marks'] = students_details[row_num][4]
            subject_student_rollno['grade'] = students_details[row_num][5]
            subject_students[students_details[row_num][0]] = subject_student_rollno

        subject_code_data['students'] = subject_students
        subject_data[code] = subject_code_data

        sub_worksheet.set_row(row_num + 5, 30)
        sub_worksheet.merge_range(row_num + 5, 0, row_num + 5, 5, 'Statistics', sub_heading_format)
        stats_row_num = row_num + 6
        sub_marks_range = xl_range(2, 4, row_num + 2, 4)
        for x in range(25):
            sub_worksheet.set_row(stats_row_num + x, 18)
            for y in range(0, 4, 3):
                sub_worksheet.merge_range(stats_row_num + x, y, stats_row_num + x, y + 2, '')
        stats_row_num += 1
        sub_worksheet.write(stats_row_num, 0, 'Total Number of students appeared', sub_left_align_format)
        sub_worksheet.write(stats_row_num, 3, number_of_students, sub_center_align_format)
        sub_worksheet.write(stats_row_num + 1, 0, 'Maximum Marks achieved', sub_left_align_format)
        sub_worksheet.write(stats_row_num + 1, 3, '=MAX({})'.format(sub_marks_range),
                            sub_center_align_format)
        sub_worksheet.write(stats_row_num + 2, 0, 'Minimum Marks achieved', sub_left_align_format)
        sub_worksheet.write(stats_row_num + 2, 3, '=MIN({})'.format(sub_marks_range),
                            sub_center_align_format)
        stats_row_num += 3
        for possible_grade in possible_grades:
            sub_worksheet.write(stats_row_num, 0, 'Number of {} s'.format(possible_grade),
                                sub_left_align_format)
            sub_worksheet.write(stats_row_num, 3, '=COUNTIF({}, "{}")'.format(xl_range(2, 5, row_num + 2, 5),
                                                                              possible_grade), sub_center_align_format)
            stats_row_num += 1
        sub_worksheet.write(stats_row_num, 0, 'Number of students obtaining >=75 marks', sub_left_align_format)
        sub_worksheet.write(stats_row_num, 3, '=COUNTIF({}, ">=75")'.format(sub_marks_range),
                            sub_center_align_format)
        sub_worksheet.write(stats_row_num + 1, 0, 'Number of students obtaining >=90 marks', sub_left_align_format)
        sub_worksheet.write(stats_row_num + 1, 3, '=COUNTIF({}, ">=90")'.format(sub_marks_range),
                            sub_center_align_format)
        stats_row_num += 2
        for marks in range(80, 30, -10):
            sub_worksheet.write(stats_row_num, 0, 'Number of students obtaining marks in the range {} to {}'
                                .format(marks, marks + 10), sub_left_align_format)
            sub_worksheet.write(stats_row_num, 3, '=COUNTIFS({}, ">={}", {}, "<{}")'
                                .format(sub_marks_range, marks, sub_marks_range, marks + 10), sub_center_align_format)
            stats_row_num += 1
        sub_worksheet.write(stats_row_num, 0, 'Number of students obtaining marks in the range 33 to 40',
                            sub_left_align_format)
        sub_worksheet.write(stats_row_num, 3, '=COUNTIFS({}, ">=33", {}, "<40")'
                            .format(sub_marks_range, sub_marks_range), sub_center_align_format)
        sub_worksheet.write(stats_row_num + 1, 0, 'Number of students obtaining marks less than 33',
                            sub_left_align_format)
        sub_worksheet.write(stats_row_num + 1, 3, '=COUNTIF({}, "<33")'
                            .format(sub_marks_range), sub_center_align_format)

    student_total_index = subject_index * 2 + 9
    main_worksheet.write(0, student_total_index, 'Student Total')

    for student_index in range(number_of_students):
        main_worksheet.set_row(student_index + 3, 18, main_left_align_format)
        main_worksheet.write_row(student_index + 3, 0, student_data[student_index][:-1])
        student_marks = list()
        english_marks = None
        for subject_code in json.loads(student_data[student_index][-1]):
            marks_data = subject_data[subject_code]['students'][student_data[student_index][0]]['marks']
            grade_data = subject_data[subject_code]['students'][student_data[student_index][0]]['grade']
            main_worksheet.write(student_index + 3,
                                 all_subjects.index((subject_data[subject_code]['subject_name'], subject_code)) * 2 + 6,
                                 marks_data)
            if 'English' in subject_data[subject_code]['subject_name']:
                english_marks = marks_data
            else:
                student_marks.append(marks_data)
            main_worksheet.write(student_index + 3,
                                 all_subjects.index((subject_data[subject_code]['subject_name'], subject_code)) * 2 + 7,
                                 grade_data)
        main_worksheet.write(student_index + 3, student_total_index, get_best(english_marks, student_marks))
    main_worksheet.set_row(row_num + 5, 30)
    main_worksheet.merge_range(number_of_students + 5, 0, number_of_students + 5, 4, 'Statistics', main_heading_format)

    main_workbook.close()
    subject_workbook.close()
    db_conn.close()


if __name__ == '__main__':
    excelify()

# TODO: Edit best calculation algorithm to account for Eng + best 4
