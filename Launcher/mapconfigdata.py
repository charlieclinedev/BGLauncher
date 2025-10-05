from collections import OrderedDict
from configparser import ConfigParser
from typing import List, Dict


class ConfigParserMultiValues(OrderedDict):
	"""Custom OrderedDict that handles multiple values for the same key."""
	
	def __setitem__(self, key, value):
		"""Set a key-value pair, extending list values if key exists."""
		if key in self and isinstance(value, list):
			self[key].extend(value)
		else:
			super().__setitem__(key, value)

	@staticmethod
	def getlist(value):
		"""Convert a string value to a list by splitting on newlines."""
		return value.split('\n')


class MapIniData:
	"""Parser for Unreal Engine map configuration data."""
	
	def __init__(self, game_ini_path: str, editor_ini_path: str) -> None:
		"""Initialize map data parser.
		
		Args:
			game_ini_path: Path to DefaultGame.ini
			editor_ini_path: Path to DefaultEditor.ini
		"""
		self.map_sections = {}
		self.all_maps = []

		print(f"Loading game config: {game_ini_path}")
		print(f"Loading editor config: {editor_ini_path}")

		try:
			game_ini = ConfigParser(strict=False, empty_lines_in_values=False, dict_type=ConfigParserMultiValues,
									converters={"list": ConfigParserMultiValues.getlist})
			game_ini.read(game_ini_path)

			if game_ini.has_section('/Script/UnrealEd.ProjectPackagingSettings'):
				maps = game_ini.getlist('/Script/UnrealEd.ProjectPackagingSettings', '+MapsToCook')
				for m in maps:
					self.all_maps.append(m.split('/')[-1][:-2])
		except Exception as e:
			print(f"Error loading game config: {e}")

		try:
			ed_ini = ConfigParser(strict=False, empty_lines_in_values=False, dict_type=ConfigParserMultiValues,
								  converters={"list": ConfigParserMultiValues.getlist})
			ed_ini.read(editor_ini_path)
			sections = ed_ini.sections()
			for section in sections:
				if ed_ini.has_option(section, '+Map') or ed_ini.has_option(section, '+Section'):
					self.map_sections[section] = []
					if ed_ini.has_option(section, '+Map'):
						maps = ed_ini.getlist(section, '+Map')
						for m in maps:
							self.map_sections[section].append(m.split('/')[-1][:-2])
					if ed_ini.has_option(section, '+Section'):
						linked_sections = ed_ini.getlist(section, '+Section')
						self.process_sections(ed_ini, linked_sections, section)
		except Exception as e:
			print(f"Error loading editor config: {e}")

	def process_sections(self, ed_ini: ConfigParser, sections: List[str], main_sec: str) -> None:
		"""Process linked sections recursively.
		
		Args:
			ed_ini: Editor INI parser
			sections: List of section names to process
			main_sec: Main section name
		"""
		for section in sections:
			if ed_ini.has_option(section, '+Map') or ed_ini.has_option(section, '+Section'):
				if ed_ini.has_option(section, '+Map'):
					maps = ed_ini.getlist(section, '+Map')
					for m in maps:
						self.map_sections[main_sec].append(m.split('/')[-1][:-2])
				if ed_ini.has_option(section, '+Section'):
					linked_sections = ed_ini.getlist(section, '+Section')
					self.process_sections(ed_ini, linked_sections, main_sec)
