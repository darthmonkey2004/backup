#!/bin/env python3

import time
import subprocess
import pickle
import PySimpleGUI as sg
import os

class backup():
	def __init__(self, backup_location=None, target_paths=[os.path.expanduser("~")], menu=False):
		self.loadmenu = menu
		self.TARGET_PATHS = target_paths
		self.CONFPATH = os.path.join(os.path.expanduser("~"), '.backups')
		self.CONFFILE = os.path.join(self.CONFPATH, 'config.dat')
		self.LOGFILE = os.path.join(self.CONFPATH, 'info.log')
		self.FOUND_BACKUPS = []
		if backup_location is None:
			try:
				self.BACKUP_LOCATION = os.path.join(self.CONFPATH, self.get_backups().reverse()[0])
				print(f"Found previous backups, using latest...({self.BACKUP_LOCATION})")
			except Exception as e:
				self.BACKUP_LOCATION = os.path.join(self.CONFPATH, "Backup_0")
				os.makedirs(self.BACKUP_LOCATION, exist_ok=True)
				print(f"No backups found! Setting default...({self.BACKUP_LOCATION})")
		else:
			self.BACKUP_LOCATION = backup_location
		self.test()
		if not os.path.exists(self.CONFFILE):
			userdir = os.path.expanduser("~")
			if userdir not in self.TARGET_PATHS:
				self.TARGET_PATHS.append(os.path.expanduser("~"))
			self.save_config()
		try:
			self.load_config()
		except:
			self.TARGET_PATHS = target_paths
			userdir = os.path.expanduser("~")
			if userdir not in self.TARGET_PATHS:
				self.TARGET_PATHS.append(os.path.expanduser("~"))
			self.save_config()
		if self.loadmenu:
			self.menu()

	def rm_path(self, paths):
		for path in paths:
			print(path, self.TARGET_PATHS)
			if type(path) == str:
				_ = self.TARGET_PATHS.pop(self.TARGET_PATHS.index(path))
			elif type(path) == int:
				_ = self.TARGET_PATHS.pop(path)
			self.WINDOW['-TARGET_PATHS-'].update(self.TARGET_PATHS)
		return self.TARGET_PATHS

	def test(self):
		if not os.path.exists(self.BACKUP_LOCATION):
			os.path.makedirs(self.BACKUP_LOCATION, exists_ok=True)
		if not os.path.exists(self.CONFPATH):
			os.path.makedirs(self.CONFPATH, exists_ok=True)

	def clean_targets(self, targets):
		l = []
		for path in targets:
			if not os.path.exists(path):
				print(f"Path not found: {path}!")
			else:
				l.append(path)
		return l
				
	def add_path(self, path):
		if not os.path.exists(path):
			print(f"Path not found: {path}!")
			return False
		else:
			self.TARGET_PATHS.append(path)
			self.WINDOW['-TARGET_PATHS-'].update(self.TARGET_PATHS)
			return True	
		
	def get_path(self):
		return sg.popup_get_folder("Select folder for backup:", title = "Select folder path...", default_path = os.getcwd(), no_window = False, size = (None, None), button_color = None, background_color = None, text_color = None, icon = None, font = None, no_titlebar = False, grab_anywhere = False, keep_on_top = None, location = (None, None), relative_location = (None, None), initial_folder = None, image = None, modal = True, history = False, history_setting_filename = None)

	def backup(self):
		self.log_data = []
		for target_dir in self.TARGET_PATHS:
			self.log_data.append(self._backup(target_dir))
		return self.log_data

	def _backup(self, target_dir):
		com = f"duplicity --no-encryption --verbosity info --log-file \"{self.LOGFILE}\" \"{target_dir}\" \"file://{self.BACKUP_LOCATION}\" >> temp.txt"
		return subprocess.call(com, shell=True)
		data = self.get_log()
		self.clear_log()
		return data

	def get_log(self):
		with open('temp.txt', 'r') as f:
			data = f.read()
			f.close()
		return data

	def clear_log(self):
		with open('temp.txt', 'w') as f:
			f.write("")
			f.close()

	def rm_log(self):
		com = f"rm \"{self.LOGFILE}\""
		return subprocess.check_output(com, shell=True).decode().strip()	

	def save_config(self):
		data = {}
		data['BACKUP_LOCATION'] = self.BACKUP_LOCATION
		data['TARGET_PATHS'] = self.TARGET_PATHS
		with open(self.CONFFILE, 'wb') as f:
			pickle.dump(data, f)
			f.close()
		print("Config saved!")

	def load_config(self):
		with open(self.CONFFILE, 'rb') as f:
			data = pickle.load(f)
			f.close()
		for k in data:
			v = data[k]
			self.__dict__[k] = v
		print("Config loaded!")

	def get_backups(self):
		l = []
		files = os.listdir(self.BACKUP_LOCATION)
		for filepath in files:
			if 'Backup_' in filepath and '.py' not in filepath:
				l.append(filepath)
		self.FOUND_BACKUPS = l
		return self.FOUND_BACKUPS

	def menu(self):
		layout = []
		listline = [[sg.Text('Directories to save:')], sg.Listbox(self.TARGET_PATHS, default_values = self.TARGET_PATHS[0], select_mode = None, change_submits = True, enable_events = True, bind_return_key = False, size = (750, 5), auto_size_text = True, key = '-TARGET_PATHS-', tooltip = "Currently selected backup sources:", expand_x = False, expand_y = False)]
		layout.append(listline)
		output = sg.Multiline(default_text = "", enter_submits = True, disabled = True, autoscroll = True, size = (75, 5), auto_size_text = True, change_submits = False, enable_events = True, key = '-OUTPUT-', auto_refresh = True, reroute_stdout = True, reroute_stderr = True, reroute_cprint = True, echo_stdout_stderr = True, tooltip = "Command output window", expand_x = False, expand_y = False, rstrip = True)
		found_backups = [[sg.Text('Current backups:')], sg.Listbox(self.get_backups(), default_values = None, select_mode = None, change_submits = True, enable_events = True, bind_return_key = False, size = (75, 5), auto_size_text = True, key = '-FOUND_BACKUPS-', tooltip = "backup file history:", expand_x = False, expand_y = False), output]
		layout.append(found_backups)
		buttons = [[sg.Button('Add Path...', key='-ADD_PATH-'), sg.Button('Remove Path', key='-REMOVE_PATH-'), sg.Text('Set Save Path:'), sg.Input(enable_events=True, expand_x=False, key='-BACKUP_LOCATION-'), sg.Button('Browse...', key='-BACKUP_LOCATION_PICKER-'), sg.Button('Set!', key='-SET_BACKUP_LOCATION-')], [sg.Button('Quit!', key='-CANCEL-'), sg.Button('Back it up!', key='-OK-')]]
		layout.append(buttons)
		self.WINDOW = sg.Window(layout=layout, title="Backups aren't scary, dad!", size=(800, 480), finalize=True)
		self.WINDOW['-BACKUP_LOCATION-'].update(self.BACKUP_LOCATION)
		self.FOUND_BACKUPS = self.get_backups()
		self.WINDOW['-FOUND_BACKUPS-'].update(self.FOUND_BACKUPS)
		self.command = None
		while True:
			event, values = self.WINDOW.read(timeout=1)
			if event != '__TIMEOUT__':
				#print(event)
				if event == '-CANCEL-':
					break
				elif event == '-OK-':
					self.save_config()
					data = self.backup()
					self.WINDOW['-OUTPUT-'].update(data)
				elif event == '-ADD_PATH-':
					path = self.add_path(self.get_path())
				elif event == '-REMOVE_PATH-':
					paths = values['-TARGET_PATHS-']
					print(type(paths), len(paths), paths)
					self.TARGET_PATHS = self.rm_path(paths)
					#print(f"Paths removed:{paths}")
					self.WINDOW['-TARGET_PATHS-'].update(self.TARGET_PATHS)
				elif event == sg.WINDOW_CLOSED:
					break
				elif event == '-SET_BACKUP_LOCATION-':
					self.BACKUP_LOCATION = values['-BACKUP_LOCATION-']
					self.save_config()
					print(f"Set backup location:{self.BACKUP_LOCATION}")
				elif event == '-BACKUP_LOCATION_PICKER-':
					path = self.get_path()
					if path is not None and path != '':
						self.WINDOW['BACKUP_LOCATION'].update(path)
						self.BACKUP_LOCATION = path
						print(f"Backup location set:{self.BACKUP_LOCATION}")
				elif event == '-OUTPUT-':
					self.command = values[event]
					#if 'command: ' in self.command:
					#	self.command = self.command.split('command: ')[1]
					#try:
					#	out = subprocess.check_output(self.command, shell=True).decode().strip()
					#	print(f"\n{out}\n")
					#except:
					#	pass
					
				
		self.WINDOW.close()
		self.save_config()
		exit()

	def parse_manifest(self):
		manifest = None
		files = os.path.listdir(self.BACKUP_LOCATION)
		out = {}
		for filepath in files:
			if '.manifest' in filepath:
				manifest = filepath
				break
		with open(manifest, 'r') as f:
			data = f.read()
			f.close()
		self.WINDOW['-BACKUP_DATA-'].update(data)
		return data

	def restore(self, src, dest_dir):
		print("TODO - build and implement restore function.")

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("-b", "--backup", help="Start auto backup. Default.", action="store_true")
	parser.add_argument("-r", "--restore", help="Restore a backup. Usage: backup.py -r 'file:///my/storage/location/Backup_??'", action="store_true")
	parser.add_argument("-l", "--location", help="Specify backup location in which to save archives.", action="store")
	parser.add_argument("-t", "--targets", help="A comma separated list of target paths (to add, incremental)", action="store")
	parser.add_argument("-m", "--menu", help="Starts configuration menu.", action="store_true")
	args = parser.parse_args()
	if not args.backup and not args.restore:
		args.menu = True
	if args.menu:
		b = backup(menu=True)
	else:
		b = backup()
	print(args.backup, args.restore, args.location)
	if args.location:
		b.BACKUP_LOCATION = args.backup
		b.save_config()
		print(f"Updated backup location: {b.BACKUP_LOCATION}")
	if args.targets:
		b.TARGET_PATHS = args.targets.split(",")
		b.save_config()
		print(f"Updated target paths! {b.TARGET_PATHS}")
	if args.restore:
		b.restore()
	elif args.backup:
		print("Starting backup...")
		b.backup()
		print("Finished backup!")
