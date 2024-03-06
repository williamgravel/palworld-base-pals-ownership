# palworld-base-pals-ownership
Tool for retrieving player ownership of guild base pals from Palworld save file.

This tool will print out the pal information (name, nickname, gender, level, max health, and boss/lucky status) of all guild base pals (or of a single guild if specified) as grouped by guild, base, and player. This tool is also capable of saving the pal ownership data to a JSON file if requested.

> [!NOTE]
> Some pals may have been owned by multiple players throughout their lifetime. This tool will only display the first player to have owned that pal (i.e. the player who first caught or hatched the pal). Such pals will be denoted by an asterisk (*) next to their name in the console printout.

## Instructions

### Prerequisites

1. Python 3.6 or newer along with any dependencies (if using the Python script)
   - You can install the latest version of Python at [python.org](https://www.python.org/)
2. Your Palworld save file converted to JSON (example: `Level.sav.json`)
   - The recommended tool for this step can be found at [github.com/cheahjs/palworld-save-tools](https://github.com/cheahjs/palworld-save-tools)

### Installation

1. Download the latest release from [Releases page](https://github.com/williamgravel/palworld-base-pals-ownership/releases/latest)
2. Uncompress the `.zip` archive into a folder

### Usage

1. Open a terminal from the uncompressed folder
2. Run the following command if using the Windows executable file (`main.exe`),
   
   ```bash
   main.exe <input_filename> [options]
   ```

   or the following command if using the Python script (`main.py`),

   ```bash
   python main.py <input_filename> [options]
   ```

   where `<input_filename>` is the converted save file (typically ending in `.sav.json`) to be processed and `[options]` are any of the below optional arguments.

#### Additional command line arguments

1. `--guild`: Specify a guild name to retrieve only base pals owned by that guild
2. `--output`: Specify an output filename to save JSON data
3. `--quiet`: Suppress console output
4. `--version`: Print version information
5. `--help`: Print help information

## Acknowledgements
Below are projects that were useful in the development of this tool:

- [cheahjs/palworld-save-tools ](https://github.com/cheahjs/palworld-save-tools) - tools for converting Palworld .sav files to JSON and back
  - Serves as a prerequisite for this tool and as an inspiration for this documentation
- [EternalWraith/PalEdit](https://github.com/EternalWraith/PalEdit) - tool for editing and generating Pals within PalWorld saves
  - Served as the source of data for the mapping of pal codenames to proper names
