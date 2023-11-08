from distutils.core import setup

setup(name='backup',
	version='1.0',
	description='Backup utility using duplicity and python3.',
	author='Matt McClellan',
	author_email='darthmonkey2004@gmail.com',
	url='http://backup.simiantech.biz/',
	packages=['backup'],
	package_dir={'backup': '.'},
	scripts=['backup.py'],
	)
