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
