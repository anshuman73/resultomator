"""
Copyright 2017, Anshuman Agarwal (Anshuman73)
Licensed under CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/)
"""

from time import time
import network_processor
import file_processor
import data_cleaner
import excelify
import os


def resultomate():
    method_choice = int(input('Choose your method of retrieving data:\n1. Network Mode\n2. Using a Text (.txt) file'
                              '\n\nYour Choice: '))
    st = None
    if method_choice not in range(1, 3):
        method_choice = 1
        print('Invalid Input, defaulting to Network Mode.')
    if method_choice == 1:
        schcode = int(input('Enter the School Code: '))
        roll_range = input('Enter range of roll numbers. Use "-" for entering ranges and use "," to separate inputs: ')
        net_choice = str(input('Go async mode for network requests ? (Y/N): ')).strip().lower()
        st = time()
        print('\n\nLog: \n')
        network_processor.process(schcode, roll_range, net_choice)
        print('\nData retrieval from network and saving raw data into database took {} seconds'.format(time() - st))
    elif method_choice == 2:
        file_address = str(input('Enter the location of the text file received in the E-Mail: '))
        st = time()
        print('\n\nLog: \n')
        file_processor.process(file_address)

    print('\n\nSaved Raw data in a Database.\n')

    print('\nProcessing and Normalizing data...\n')
    data_cleaner.clean()
    print('\nData successfully Normalized\n')

    print('\nDumping data to excel files...\n')
    excelify.excelify()

    print('\nDeleting databases')
    [os.remove(db_file) for db_file in os.listdir(os.getcwd()) if db_file.endswith('.sqlite')]
    print('All databases deleted !\n')

    print('\nFinished processing everything.')
    print('Took {} seconds for execution\n'.format(time() - st))

    input('Press Enter to exit: ')

if __name__ == '__main__':
    resultomate()
