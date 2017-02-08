"""
Copyright 2017, Anshuman Agarwal (Anshuman73)
Licensed under CC BY-NC-ND 4.0 (https://creativecommons.org/licenses/by-nc-nd/4.0/)
"""

from time import time
import os
import extractor
import cleaner
import visualizer


def main():
    schcode = int(input('Enter the School Code: '))
    lwr = int(input('Enter the lower limit of the Roll Numbers: '))
    upr = int(input('Enter the upper limit of the Roll Numbers: '))
    net_choice = str(input('Go async mode for network requests ? (Y/N): ')).strip().lower()
    st = time()

    print('\n\nLog: \n')

    extractor.extract(schcode, lwr, upr, net_choice)
    print('\nData retrieval from network took {} seconds'.format(time() - st))
    print('\n\nSaved Raw data in a Database.\n')

    print('\nProcessing and Normalizing data...\n')
    cleaner.clean()
    print('\nData successfully Normalized\n')
    print('\nDeleting raw database')
    os.remove(os.getcwd() + '/raw_data.sqlite')
    print('Raw database deleted !\n')

    print('\nDumping data to excel files...\n')
    visualizer.excelify()

    print('\nFinished processing everything.')
    print('Took {} seconds for execution\n'.format(time() - st))

    input('Press Enter to exit: ')

if __name__ == '__main__':
    main()
