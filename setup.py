from setuptools import setup

setup(name='Resultomator',
      version='1.0',
      description='Get cbse results analysis',
      author='Anshuman Agarwal',
      author_email='dev.anshuman73@gmail.com',
      url='anshuman73.github.io',
      install_requires=['Flask==0.10.1', 'MarkupSafe==0.23', 'beautifulsoup4==4.6.0', 'gevent==1.2.1', 'greenlet==0.4.12', 'grequests==0.3.0', 'requests==2.14.2', 'XlsxWriter==0.9.6'],
      )
