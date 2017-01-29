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


def main():
    schcode = int(input('Enter the School Code: '))
    lwr = int(input('Enter the lower limit of the Roll Numbers: '))
    upr = int(input('Enter the upper limit of the Roll Numbers: '))
    st = time()

    print('\n\nLog: \n')

    extractor.extract(schcode, lwr, upr)
    print('\nSaved Raw data in a Database. ')

    print('\nProcessing and Normalizing data...')
    cleaner.clean()
    print('\n\nData successfully Normalized\n')
    print('Deleting raw database')
    os.remove(os.getcwd() + '/raw_data.sqlite')
    print('Raw database deleted !\n')

    print('\nReady to visualize data...\n')

    # Write viz code / call the functions from module

    print('\nFinished processing everything.\n')
    print('\nTook {} seconds for execution'.format(time() - st))

    try:
        input('Press Enter to exit: ')
    except SyntaxError:  # Stupid Python 2 compatibility
            pass

if __name__ == '__main__':
    main()
