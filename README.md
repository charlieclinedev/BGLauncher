# BGLauncher

A dynamic GUI launcher for running Unreal Engine BuildGraph commands with an intuitive interface for managing build configurations, map selections, and platform-specific builds.

## Features

- **Dynamic UI Generation**: Automatically generates UI controls based on BuildGraph XML configuration
- **Multi-Platform Support**: Handles PlayStation, Xbox, and PC platform builds
- **Map Management**: Integrated map selection and section-based map grouping
- **Configuration Persistence**: Saves and restores user settings between sessions
- **Real-time Build Execution**: Launch and monitor multiple build processes
- **Debug Mode**: Toggle debug mode with F9 key for build validation
- **Process Management**: Kill all running processes with F11 key

## Requirements

- Python 3.6+
- Unreal Engine project with BuildGraph setup
- Windows (for Unreal Engine integration)

## Installation

1. Clone or download this repository
2. Ensure your Unreal Engine project has BuildGraph XML files in the `BuildGraph/` directory
3. Run the launcher with your project paths

## Usage

### Basic Usage

```bash
python launcher.py <script_directory> <project_directory>
```

**Parameters:**
- `script_directory`: Path to directory containing BuildGraph XML files
- `project_directory`: Base directory of your Unreal Engine project

### Example

```bash
python launcher.py "C:\MyProject\BuildGraph" "C:\MyProject"
```

### UI Sections

The launcher organizes controls into logical sections:

- **General**: Basic build settings and options
- **Package**: Packaging and deployment settings
- **Maps**: Map selection and configuration
- **Compile**: Compilation settings
- **Editor**: Editor-specific options

### Keyboard Shortcuts

- **F9**: Toggle debug mode (changes background color)
- **F11**: Kill all running build processes

## BuildGraph XML Configuration

The launcher reads BuildGraph XML files to dynamically generate the UI. Your XML files should follow this format:

### Option Format
```xml
<Option Name="OptionName" DefaultValue="default" Restrict="option1|option2|option3">
    [Category][Type][Extra] Description text
</Option>
```

**Supported Types:**
- `TextEntry`: Text input field
- `Dropdown`: Dropdown selection
- `Checkbox`: Boolean checkbox
- `DirectoryChooser`: Directory selection with browse button
- `MapSelect`: Map selection with add/remove functionality
- `MapSectionSelect`: Section-based map selection
- `MultiSelect`: Multiple option selection

### Aggregate Format
```xml
<Aggregate Name="ActionName" Label="[Category] Action Description">
    <!-- BuildGraph action definition -->
</Aggregate>
```

## File Structure

```
BGLauncher/
├── Launcher/
│   ├── launcher.py          # Main application entry point
│   ├── launcherwindow.py    # GUI window and layout management
│   ├── buildgraphapi.py     # BuildGraph XML parsing
│   ├── mapconfigdata.py     # Unreal Engine map configuration
│   ├── uicomponent.py       # UI component classes
│   └── tooltip.py           # Tooltip functionality
├── BuildGraph/
│   ├── GlobalVariables.xml  # Global build variables
│   ├── CPG_Builds.xml       # Main build actions
│   ├── Platform_PS4.xml     # PlayStation 4 specific builds
│   ├── Platform_PS5.xml     # PlayStation 5 specific builds
│   ├── Platform_XBoxOne.xml # Xbox One specific builds
│   └── Platform_XSX.xml      # Xbox Series X specific builds
└── README.md
```

## Configuration

The launcher automatically saves your settings to:
```
<project_directory>/unreal/Game/Saved/Launcher.ini
```

Settings are organized by category and persist between sessions.

## Map Configuration

The launcher reads map information from your Unreal Engine project's INI files:

- **DefaultGame.ini**: Contains the main map list for cooking
- **DefaultEditor.ini**: Contains map sections and groupings

### Map Sections

Map sections allow you to group related maps together. Define them in `DefaultEditor.ini`:

```ini
[MyMapSection]
+Map=/Game/Maps/Map1
+Map=/Game/Maps/Map2
+Section=LinkedSection
```

## Build Process

When you click a build button, the launcher:

1. Saves current configuration
2. Constructs the RunUAT command with all parameters
3. Launches the build process in a separate thread
4. Allows multiple builds to run simultaneously

### Command Structure

```bash
<engine_dir>/Engine/Build/BatchFiles/RunUAT.bat BuildGraph
    -set:CheckoutPath=<project_dir>
    -set:ProjectDir=<game_dir>
    -script=<graph_script>
    -target=<action_name>
    -set:<option_name>=<value>
    [-listonly]  # If debug mode is enabled
```

## Error Handling

The launcher includes comprehensive error handling for:

- XML parsing errors
- File access issues
- Build process failures
- Configuration save/load errors

Errors are logged to the console with descriptive messages.

## Development

### Adding New UI Components

1. Create a new class inheriting from `BaseOption` in `uicomponent.py`
2. Implement the `elem_init()` method for UI setup
3. Override `get_value()` and `set_value()` if needed
4. Add the new type to the option parsing in `buildgraphapi.py`

### Adding New BuildGraph Types

1. Add the new type to the `BuildGraphOption` parsing
2. Add UI creation logic in `launcherwindow.py`
3. Update the `MainApp` initialization to handle the new type

## Troubleshooting

### Common Issues

1. **XML Parsing Errors**: Check that your BuildGraph XML files are valid
2. **Map Loading Issues**: Verify that your Unreal Engine INI files exist and are accessible
3. **Build Failures**: Check that RunUAT.bat exists in your engine directory
4. **Configuration Not Saving**: Ensure the launcher has write permissions to the project directory

### Debug Mode

Enable debug mode with F9 to:
- See the exact command that would be executed
- Validate your BuildGraph configuration
- Troubleshoot parameter issues

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests. When contributing:

1. Follow the existing code style
2. Add appropriate docstrings
3. Include error handling
4. Test with your BuildGraph setup