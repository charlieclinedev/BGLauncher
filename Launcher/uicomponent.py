import tkinter as tk
from configparser import ConfigParser
from tkinter.filedialog import askdirectory
from typing import Any, Dict, List

import buildgraphapi
import tooltip


class BaseOption:
	"""Base class for all UI option components."""
	
	def __init__(self, window: tk.Widget, bg_option: Any) -> None:
		"""Initialize base option.
		
		Args:
			window: Parent window
			bg_option: BuildGraph option data
		"""
		self.option = bg_option
		self.name = bg_option.name
		self.selected = tk.StringVar(window, bg_option.default)
		self.ui = tk.Frame(window)
		tooltip.Tooltip(self.ui, text=bg_option.description)
		self.elem_init(bg_option)

	def elem_init(self, bg_option):
		"""Initialize the specific UI element. Override in subclasses."""
		pass

	def get_value(self, context: str) -> str:
		"""Get the current value of the option."""
		return self.selected.get()

	def set_value(self, value: str) -> None:
		"""Set the value of the option."""
		self.selected.set(value)

	def save_config(self, config_parser: ConfigParser) -> None:
		"""Save option value to configuration."""
		if not config_parser.has_section(self.option.category):
			config_parser.add_section(self.option.category)
		config_parser.set(self.option.category, self.name, self.get_value('self'))

	def load_config(self, config_parser: ConfigParser) -> None:
		"""Load option value from configuration."""
		if config_parser.has_option(self.option.category, self.name):
			self.set_value(config_parser.get(self.option.category, self.name))


class DropdownOption(BaseOption):
	"""Dropdown/combobox option component."""
	
	def elem_init(self, bg_option):
		"""Initialize dropdown UI elements."""
		lbl = tk.Label(self.ui, text=self.name)
		elm = tk.OptionMenu(self.ui, self.selected, *bg_option.restrict)
		lbl.pack(side=tk.LEFT)
		elm.pack(side=tk.LEFT)


class TextEntryOption(BaseOption):
	"""Text entry option component."""
	
	def elem_init(self, bg_option):
		"""Initialize text entry UI elements."""
		lbl = tk.Label(self.ui, text=self.name)
		elm = tk.Entry(self.ui, textvariable=self.selected)
		lbl.pack(side=tk.LEFT)
		elm.pack(side=tk.LEFT)


class CheckboxOption(BaseOption):
	"""Checkbox option component."""
	
	def elem_init(self, bg_option):
		"""Initialize checkbox UI elements."""
		self.selected.set(bg_option.default.lower())
		elm = tk.Checkbutton(self.ui, text=self.name, variable=self.selected, onvalue='true', offvalue='false')
		elm.pack(side=tk.LEFT)


class DirectoryOption(BaseOption):
	"""Directory chooser option component."""
	
	def elem_init(self, bg_option):
		"""Initialize directory chooser UI elements."""
		lbl = tk.Label(self.ui, text=self.name)
		elm = tk.Entry(self.ui, textvariable=self.selected)
		btn = tk.Button(self.ui, text='...', command=self.choose_output_dir)
		lbl.pack(side=tk.LEFT)
		elm.pack(side=tk.LEFT)
		btn.pack(side=tk.LEFT)

	def choose_output_dir(self):
		"""Open directory chooser dialog."""
		self.selected.set(askdirectory())


class MapSelectOption(BaseOption):
	"""Map selection option component."""
	
	def __init__(self, window, bg_option, map_data):
		"""Initialize map selection option.
		
		Args:
			window: Parent window
			bg_option: BuildGraph option data
			map_data: Map configuration data
		"""
		self.map_data = map_data
		self.selected_map = None
		self.map_list = None
		super().__init__(window, bg_option)

	def elem_init(self, bg_option):
		self.selected_map = tk.StringVar(self.ui, 'Seventh_Sanctum_P')
		frame = tk.Frame(self.ui)
		frame.pack(fill=tk.BOTH)

		lbl = tk.Label(frame, text=self.name)
		lbl.grid(row=0, column=0, columnspan=4)
		opt = tk.OptionMenu(frame, self.selected_map, *self.map_data.all_maps)
		opt.grid(row=1, column=1, sticky='n')
		btn = tk.Button(frame, text=">>>", command=self.add_map)
		btn.grid(row=1, column=2, sticky='s')
		btn = tk.Button(frame, text="<<<", command=self.remove_map)
		btn.grid(row=2, column=2, sticky='n')

		self.map_list = tk.Listbox(frame, selectmode='multiple')
		self.map_list.grid(row=1, column=3, rowspan=2, sticky='nswe')

	def add_map(self):
		"""Add selected map to the list."""
		self.map_list.insert(0, self.selected_map.get())

	def remove_map(self):
		"""Remove selected maps from the list."""
		selected = self.map_list.curselection()
		for index in selected:
			self.map_list.delete(index)

	def get_value(self, context):
		selected_maps = []
		if context == 'Fill DDC' and self.map_list.size() == 0:
			for m in self.map_data.all_maps:
				selected_maps.append(m)
		else:
			for m in self.map_list.get(0, self.map_list.size()):
				selected_maps.append(m)
		return '+'.join(selected_maps)

	def set_value(self, value):
		ml = value.split('+')
		for m in ml:
			if m != '':
				self.map_list.insert(self.map_list.size() + 1, m)


class MultiSelectOption(BaseOption):
	"""Multi-select option component."""
	
	def __init__(self, window, bg_option):
		"""Initialize multi-select option."""
		self.all_options = {}
		self.delimiter = ';'
		super().__init__(window, bg_option)

	def elem_init(self, bg_option):
		if ';' in bg_option.default:
			self.delimiter = ';'
		elif ',' in bg_option.default:
			self.delimiter = ','
		elif '+' in bg_option.default:
			self.delimiter = '+'
		options = bg_option.default.split(self.delimiter)

		cur_row = 0
		cur_col = 0
		lbl = tk.Label(self.ui, text=self.name)
		lbl.grid(row=cur_row, column=cur_col, sticky='w')
		cur_col += 1
		for op in options:
			self.all_options[op] = tk.StringVar(self.ui, 'true')
			elm = tk.Checkbutton(self.ui, text=op, variable=self.all_options[op], onvalue='true', offvalue='false')
			elm.grid(row=cur_row, column=cur_col, sticky='w')
			cur_row += 1

	def get_value(self, context):
		selected_options = []
		for key in self.all_options:
			if self.all_options[key].get() == 'true':
				selected_options.append(key)
		return self.delimiter.join(selected_options)

	def set_value(self, value):
		sl = value.split(self.delimiter)
		for key in self.all_options:
			if key in sl:
				self.all_options[key].set('true')
			else:
				self.all_options[key].set('false')


class MapSectionSelectOption(BaseOption):
	"""Map section selection option component."""
	
	def __init__(self, window, bg_option, map_data):
		"""Initialize map section selection option.
		
		Args:
			window: Parent window
			bg_option: BuildGraph option data
			map_data: Map configuration data
		"""
		self.map_data = map_data
		self.map_sections = {}
		super().__init__(window, bg_option)

	def elem_init(self, bg_option):
		cur_row = 0
		cur_col = 0
		map_row = 0
		lbl = tk.Label(self.ui, text=self.name)
		lbl.pack()
		map_frame = tk.Frame(self.ui)
		map_frame.pack()
		for map_section in self.map_data.map_sections:
			self.map_sections[map_section] = tk.StringVar(map_frame, 'false')
			section_btn = tk.Checkbutton(map_frame, text=map_section,
									  variable=self.map_sections[map_section], onvalue='true', offvalue='false')
			section_btn.grid(row=cur_row + map_row, column=cur_col, sticky="w")

			tooltip.Tooltip(section_btn, text='\n'.join(self.map_data.map_sections[map_section]))

			map_row += 1
			if map_row >= 4:
				map_row = 0
				cur_col += 1

	def get_value(self, context):
		if context == 'Fill DDC':
			return ''
		selected_sections = []
		for key in self.map_sections:
			if self.map_sections[key].get() == 'true':
				selected_sections.append(key)
		return '+'.join(selected_sections)

	def set_value(self, value):
		sl = value.split('+')
		for key in self.map_sections:
			if key in sl:
				self.map_sections[key].set('true')
			else:
				self.map_sections[key].set('false')


class RunButton:
	"""Button component for running build actions."""
	
	def __init__(self, window, bg_node, on_pressed):
		"""Initialize run button.
		
		Args:
			window: Parent window
			bg_node: BuildGraph node data
			on_pressed: Callback for button press
		"""
		self.name = bg_node.name
		self.pressed_callback = on_pressed
		self.ui = tk.Button(window, text=self.name, command=self.on_button_pressed)
		tooltip.Tooltip(self.ui, text=bg_node.description)

	def on_button_pressed(self):
		"""Handle button press event."""
		self.pressed_callback(self.name)
