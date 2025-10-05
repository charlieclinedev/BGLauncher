import argparse
import os
import signal
import subprocess
from configparser import ConfigParser
from typing import List, Callable

import buildgraphapi
from launcherwindow import LauncherWindow
from mapconfigdata import MapIniData

parser = argparse.ArgumentParser()
parser.add_argument('script_directory', help="Base directory where scripts are held")
parser.add_argument('project_directory', help="Base checkout directory")
args = parser.parse_args()


class MainApp:
	"""Main application class for the BuildGraph launcher."""
	
	def __init__(self, in_script_dir: str, in_project_dir: str):
		"""Initialize the main application.
		
		Args:
			in_script_dir: Directory containing BuildGraph scripts
			in_project_dir: Base project directory
		"""
		self.threads = []
		self.script_dir = in_script_dir
		self.project_dir = in_project_dir
		self.game_dir = os.path.join(self.project_dir, 'unreal', 'Game')
		self.engine_dir = os.path.join(self.project_dir, 'unreal')
		self.graph_script = os.path.join(self.script_dir, 'CPG_Builds.xml')
		self.platform_scripts = [
			os.path.join(self.script_dir, 'Platform_PS4.xml'),
			os.path.join(self.script_dir, 'Platform_PS5.xml'),
			os.path.join(self.script_dir, 'Platform_XBoxOne.xml'),
			os.path.join(self.script_dir, 'Platform_XSX.xml'),
		]
		self.config_ini = os.path.join(self.game_dir, 'Saved', 'Launcher.ini')
		self.launcher_window = LauncherWindow(self.on_exit, self.on_key_pressed)

		bg = buildgraphapi.BuildGraph(os.path.join(self.script_dir, 'GlobalVariables.xml'),
									  self.graph_script, self.platform_scripts)

		map_data = MapIniData(os.path.join(self.game_dir, 'Config', 'DefaultGame.ini'),
							  os.path.join(self.game_dir, 'Config', 'DefaultEditor.ini'))

		for elm in bg.options:
			if elm.type == 'TextEntry':
				self.launcher_window.add_entry(elm)
			elif elm.type == 'Dropdown':
				self.launcher_window.add_dropdown(elm)
			elif elm.type == 'Checkbox':
				self.launcher_window.add_checkbox(elm)
			elif elm.type == 'DirectoryChooser':
				self.launcher_window.add_directory_choice(elm)
			elif elm.type == 'MapSelect':
				self.launcher_window.add_map_select(elm, map_data)
			elif elm.type == 'MapSectionSelect':
				self.launcher_window.add_map_section_select(elm, map_data)
			elif elm.type == 'MultiSelect':
				self.launcher_window.add_multi_select(elm)

		for node in bg.actions:
			self.launcher_window.add_button(node, self.on_button_pressed)

		self.launcher_window.position_all()
		self.load_config()

	def on_key_pressed(self, key) -> None:
		"""Handle key press events.
		
		Args:
			key: The key event object
		"""
		if key.keysym == 'F11':
			self.kill_all_proc()

	def on_button_pressed(self, name: str) -> None:
		"""Handle button press events to start build processes.
		
		Args:
			name: Name of the build target to execute
		"""
		try:
			self.save_config()
			proc = [f'{self.engine_dir}/Engine/Build/BatchFiles/RunUAT.bat',
					'BuildGraph',
					f'-set:CheckoutPath={self.project_dir}',
					f'-set:ProjectDir={self.game_dir}',
					f'-script={self.graph_script}',
					f'-target={name}']
			for opt in self.launcher_window.ui_list:
				val = opt.get_value(name)
				if len(val) > 0:
					param = f'-set:{opt.name}={val}'
					proc.append(param)

			if self.launcher_window.debug:
				proc.append('-listonly')

			self.threads.append(subprocess.Popen(proc, shell=True))
		except Exception as e:
			print(f"Error starting build process: {e}")
			# Could add a message box here to inform the user

	def launch(self) -> None:
		"""Start the launcher window."""
		self.launcher_window.start()

	def kill_all_proc(self) -> None:
		"""Terminate all running build processes."""
		print('terminating threads')
		for t in self.threads:
			t.send_signal(signal.CTRL_C_EVENT)
		self.threads = []

	def on_exit(self) -> None:
		"""Handle application exit."""
		self.save_config()
		if len(self.threads) > 0:
			if self.launcher_window.ask_question('Exit Program', 'Would you like to end all spawned processes?'):
				self.kill_all_proc()
		self.launcher_window.exit()

	def save_config(self) -> None:
		"""Save current configuration to file."""
		try:
			config_parser = ConfigParser()
			self.launcher_window.save_config(config_parser)
			with open(self.config_ini, 'w') as fp:
				config_parser.write(fp)
		except Exception as e:
			print(f"Error saving configuration: {e}")

	def load_config(self) -> None:
		"""Load configuration from file."""
		try:
			config_parser = ConfigParser()
			if config_parser.read(self.config_ini):
				self.launcher_window.load_config(config_parser)
		except Exception as e:
			print(f"Error loading configuration: {e}")


main_app = MainApp(args.script_directory, args.project_directory)
main_app.launch()
