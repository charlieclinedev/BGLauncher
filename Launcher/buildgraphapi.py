import re
import xml.etree.ElementTree as et
from typing import List, Optional, Tuple

ns = {'BuildGraph': 'http://www.epicgames.com/BuildGraph'}


class BuildGraphOption:
	"""Represents a BuildGraph option with metadata."""
	
	def __init__(self, opt) -> None:
		"""Initialize a BuildGraph option.
		
		Args:
			opt: XML element containing option data
		"""
		self.name = opt.get('Name')
		self.default = opt.get('DefaultValue')
		r = opt.get('Restrict')
		if r:
			self.restrict = tuple(r.split('|'))
		else:
			self.restrict = None
		self.description = opt.get('Description')
		parsed = re.findall('\[.*?\]', self.description)

		self.category = None
		if len(parsed) >= 1:
			self.category = parsed[0].replace('[', '').replace(']', '')

		self.type = None
		if len(parsed) >= 2:
			self.type = parsed[1].replace('[', '').replace(']', '')

		self.extra = None
		if len(parsed) >= 3:
			self.extra = parsed[2].replace('[', '').replace(']', '')

		for p in parsed:
			self.description = self.description.replace(p, '')


class BuildGraphAggregate:
	"""Represents a BuildGraph aggregate (action/target)."""
	
	def __init__(self, item) -> None:
		"""Initialize a BuildGraph aggregate.
		
		Args:
			item: XML element containing aggregate data
		"""
		self.name = item.get('Name')
		self.description = item.get('Label')
		if not self.description:
			return

		parsed = re.findall('\[.*?\]', self.description)

		self.category = None
		if len(parsed) >= 1:
			self.category = parsed[0].replace('[', '').replace(']', '')

		for p in parsed:
			self.description = self.description.replace(p, '')


class BuildGraph:
	"""Main BuildGraph parser and configuration manager."""
	
	def __init__(self, var_file: str, action_file: str, platform_files: List[str]) -> None:
		"""Initialize BuildGraph parser.
		
		Args:
			var_file: Path to global variables XML file
			action_file: Path to main actions XML file
			platform_files: List of platform-specific XML files
		"""
		self.options = []
		self.actions = []
		
		try:
			# Parse global variables
			tree = et.parse(var_file)
			root = tree.getroot()
			for child in root.findall('BuildGraph:Option', ns):
				option = BuildGraphOption(child)
				if option.type:
					self.options.append(option)
		except Exception as e:
			print(f"Error parsing variables file {var_file}: {e}")
		
		try:
			# Parse main actions
			tree = et.parse(action_file)
			root = tree.getroot()
			for child in root.findall('BuildGraph:Aggregate', ns):
				item = BuildGraphAggregate(child)
				if item.description and item.category:
					self.actions.append(item)
		except Exception as e:
			print(f"Error parsing actions file {action_file}: {e}")
		
		# Parse platform files
		for file in platform_files:
			try:
				tree = et.parse(file)
				root = tree.getroot()
				for child in root.findall('BuildGraph:Aggregate', ns):
					item = BuildGraphAggregate(child)
					if item.description and item.category:
						self.actions.append(item)
			except Exception as e:
				print(f"Error parsing platform file {file}: {e}")
