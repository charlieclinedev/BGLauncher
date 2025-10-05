import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

import uicomponent


class Section:
	"""UI section container for organizing related controls."""
	
	def __init__(self, window, in_name, num_col=1):
		"""Initialize a UI section.
		
		Args:
			window: Parent window
			in_name: Section name
			num_col: Number of columns for layout
		"""
		self.name = in_name
		self.num_col = num_col
		self.ui = tk.Frame(window)
		self.ui_list = []

	def position_all(self):
		rows_per_col = int(len(self.ui_list) / self.num_col)
		total_rows = 2 + 1 + rows_per_col + 1
		total_col = self.num_col + 2
		cur_row = 0
		cur_col = 0
		col_span = 1
		row_span = total_rows
		sep = ttk.Separator(self.ui, orient='vertical')
		sep.grid(row=cur_row, column=cur_col, columnspan=col_span, rowspan=row_span, sticky='nwse')

		col_span = total_col
		row_span = 1
		sep = ttk.Separator(self.ui, orient='horizontal')
		sep.grid(row=cur_row, column=cur_col, columnspan=col_span, rowspan=row_span, sticky='nwse')

		cur_row = 1
		cur_col = 1
		col_span = self.num_col
		row_span = 1
		lbl = tk.Label(self.ui, text=self.name)
		lbl.grid(row=cur_row, column=cur_col, columnspan=col_span, rowspan=row_span, sticky='nwse')

		cur_row += 1
		col_span = self.num_col
		sep = ttk.Separator(self.ui, orient='horizontal')
		sep.grid(row=cur_row, column=cur_col, columnspan=col_span, rowspan=row_span, sticky='nwse')

		cur_row += 1
		col_span = 1
		list_row = 0
		for ui_elem in self.ui_list:
			ui_elem.ui.grid(row=cur_row+list_row, column=cur_col, columnspan=col_span, rowspan=row_span, sticky='nwse')
			list_row += 1
			if list_row > rows_per_col:
				cur_col += 1
				list_row = 0

		cur_row = 0
		cur_col = total_col
		col_span = 1
		row_span = total_rows
		sep = ttk.Separator(self.ui, orient='vertical')
		sep.grid(row=cur_row, column=cur_col, columnspan=col_span, rowspan=row_span, sticky='nwse')

		cur_row = total_rows
		cur_col = 0
		col_span = total_col
		row_span = 1
		sep = ttk.Separator(self.ui, orient='horizontal')
		sep.grid(row=cur_row, column=cur_col, columnspan=col_span, rowspan=row_span, sticky='nwse')


class LauncherWindow:
	"""Main launcher window containing all UI controls."""
	
	def key_release(self, key):
		"""Handle key release events.
		
		Args:
			key: The key event object
		"""
		if key.keysym == 'F9':
			if not self.debug:
				self.window.configure(bg=self.debug_color)
				self.debug = True
			else:
				self.window.configure(bg=self.normal_color)
				self.debug = False
		else:
			self.on_key_press(key)

	def __init__(self, on_exit, on_key_press):
		"""Initialize the launcher window.
		
		Args:
			on_exit: Callback for exit events
			on_key_press: Callback for key press events
		"""
		self.debug = False
		self.on_key_press = on_key_press
		self.window = tk.Tk()
		self.window.title('Launcher')
		self.window.geometry('230x180')
		self.window.protocol("WM_DELETE_WINDOW", on_exit)

		self.normal_color = self.window['bg']
		self.debug_color = '#4f4d48'

		self.window.bind('<KeyRelease>', self.key_release)

		self.ui_list = []
		self.btn_list = []
		self.sections = {'General': Section(self.window, 'General'),
						 'Package': Section(self.window, 'Package', 2),
						 'Maps': Section(self.window, 'Maps'),
						 'Compile': Section(self.window, 'Compile'),
						 'Editor': Section(self.window, 'Editor')}
		self.sections['General'].ui.grid(row=0, column=0, rowspan=2, sticky='nw')
		self.sections['Compile'].ui.grid(row=0, column=1, sticky='nw')
		self.sections['Package'].ui.grid(row=1, column=1, sticky='nw')
		self.sections['Maps'].ui.grid(row=0, column=2, rowspan=2, columnspan=2, sticky='nw')
		self.sections['Editor'].ui.grid(row=0, column=4, rowspan=2, columnspan=1, sticky='nw')
		self.btn_sections = {'Cook': Section(self.window, 'Cook', 2),
						 'Package': Section(self.window, 'Package', 2),
						 'Test': Section(self.window, 'Test', 2),
						 'Compile': Section(self.window, 'Compile', 2),
						 'Editor': Section(self.window, 'Editor', 2)}
		sep = ttk.Separator(self.window, orient='horizontal')
		sep.grid(row=2, column=0, columnspan=6, sticky='nwse')
		self.btn_sections['Cook'].ui.grid(row=3, column=0, sticky='n')
		self.btn_sections['Package'].ui.grid(row=3, column=1, sticky='n')
		self.btn_sections['Test'].ui.grid(row=3, column=2, sticky='n')
		self.btn_sections['Compile'].ui.grid(row=3, column=3, sticky='n')
		self.btn_sections['Editor'].ui.grid(row=3, column=4, sticky='n')

	def exit(self):
		"""Close the launcher window."""
		self.window.destroy()

	@staticmethod
	def ask_question(title, question):
		"""Display a yes/no question dialog.
		
		Args:
			title: Dialog title
			question: Question text
			
		Returns:
			bool: True if user clicked yes
		"""
		response = messagebox.askquestion(title, question)
		print(response)
		return response == 'yes'

	def add_dropdown(self, bg_option):
		dp = uicomponent.DropdownOption(self.sections[bg_option.category].ui, bg_option)
		self.ui_list.append(dp)
		self.sections[bg_option.category].ui_list.append(dp)

	def add_entry(self, bg_option):
		dp = uicomponent.TextEntryOption(self.sections[bg_option.category].ui, bg_option)
		self.ui_list.append(dp)
		self.sections[bg_option.category].ui_list.append(dp)

	def add_checkbox(self, bg_option):
		dp = uicomponent.CheckboxOption(self.sections[bg_option.category].ui, bg_option)
		self.ui_list.append(dp)
		self.sections[bg_option.category].ui_list.append(dp)

	def add_directory_choice(self, bg_option):
		dp = uicomponent.DirectoryOption(self.sections[bg_option.category].ui, bg_option)
		self.ui_list.append(dp)
		self.sections[bg_option.category].ui_list.append(dp)

	def add_map_select(self, bg_option, map_data):
		dp = uicomponent.MapSelectOption(self.sections[bg_option.category].ui, bg_option, map_data)
		self.ui_list.append(dp)
		self.sections[bg_option.category].ui_list.append(dp)

	def add_map_section_select(self, bg_option, map_data):
		dp = uicomponent.MapSectionSelectOption(self.sections[bg_option.category].ui, bg_option, map_data)
		self.ui_list.append(dp)
		self.sections[bg_option.category].ui_list.append(dp)

	def add_multi_select(self, bg_option):
		dp = uicomponent.MultiSelectOption(self.sections[bg_option.category].ui, bg_option)
		self.ui_list.append(dp)
		self.sections[bg_option.category].ui_list.append(dp)

	def add_button(self, bg_node, on_pressed):
		dp = uicomponent.RunButton(self.btn_sections[bg_node.category].ui, bg_node, on_pressed)
		self.btn_list.append(dp)
		self.btn_sections[bg_node.category].ui_list.append(dp)

	def position_all(self):
		for key in self.sections:
			self.sections[key].position_all()
		for key in self.btn_sections:
			self.btn_sections[key].position_all()

	def save_config(self, config_parser):
		for ui_elem in self.ui_list:
			ui_elem.save_config(config_parser)

	def load_config(self, config_parser):
		for ui_elem in self.ui_list:
			ui_elem.load_config(config_parser)

	def start(self):
		self.window.geometry("")
		try:
			self.window.mainloop()
		except KeyboardInterrupt:
			self.start()
