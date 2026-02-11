# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Serato-tools is a Python library for parsing and modifying Serato DJ software files, including:
- Track metadata (hot cues, beatgrid, waveform, track color, autogain)
- Library database files
- Crates and Smart Crates
- Dynamic beatgrid analysis (similar to Rekordbox)
- USB export functionality

The project requires Python 3.12+ and is published to PyPI as `serato-tools`.

## Development Commands

### Setup
```bash
# Install in editable mode with all optional dependencies
pip install -e ".[track_tags,waveform_drawing,beatgrid_analysis]"

# Install linting tools
pip install pylint
```

### Linting & Formatting
```bash
# Run Pylint (max line length: 120)
pylint $(git ls-files '*.py')

# Run PyRight type checker
pyright

# Format with Black (line length: 120)
black .
```

### Testing
```bash
# Run all tests
python -m unittest

# Run specific test file
python -m unittest test.test_crate

# Run specific test case
python -m unittest test.test_crate.TestCase.test_parse_and_modify_and_dump
```

### CLI Commands
The package provides several CLI entry points (defined in pyproject.toml):
```bash
serato_analyze_beatgrid "path/to/track.mp3"
serato_usb_export --drive E --crate_matcher *house* *techno* --root_crate="USB Crate Name"
serato_smartcrate "path/to/SmartCrate.scrate" --set_rules --grouping UNTAGGED
serato_crate "path/to/Crate.crate"
```

## Code Architecture

### Core Base Classes

**`SeratoBinFile` (utils/bin_file_base.py)**
- Base class for all Serato binary file parsing
- Handles reading/writing binary data with struct-based parsing
- Defines `Fields` as StrEnum for field identifiers (e.g., "vrsn", "otrk", "pfil")
- Core data structure: `Entry = tuple[ParsedField, Value]` and `EntryList = list[Entry]`
- Supports nested entries (values can be BasicValue or EntryList)
- Provides methods: `_parse_item()`, `_build_item()`, `get_entries()`, `modify_entries()`
- Can serialize to/from JSON for debugging

**`CrateBase` (utils/crate_base.py)**
- Extends `SeratoBinFile` for crate and smart crate files
- Adds track path handling methods
- Provides `get_track_paths()` and `print_track_paths()`

### Main Modules

**Track Modules** (all extend functionality for reading/writing Serato GEOB tags in audio files):
- `track_cues_v2.py` - Main module for hot cues, loops, track color (Serato Markers2 tag)
- `track_cues_v1.py` - Legacy cues format (Serato Markers_ tag)
- `track_beatgrid.py` - Beatgrid markers, includes dynamic analysis (Serato BeatGrid tag)
- `track_autotags.py` - BPM and gain values (Serato Autotags tag)
- `track_waveform.py` - Waveform data (Serato Overview tag)
- `track_tagdump.py` - Debug tool to dump all tag data

**Library Management**:
- `database_v2.py` - Parse/modify Serato library database (database V2 files)
- `crate.py` - Regular crates (.crate files)
- `smart_crate.py` - Smart crates with rules (.scrate files)
- `usb_export.py` - Export crates to USB (smarter than Serato's built-in sync)

**Utilities**:
- `utils/beatgrid_analyze.py` - Dynamic beatgrid analysis using librosa and numpy
- `utils/track_tags.py` - Helper functions for mutagen tag operations
- `utils/ui.py` - UI/console output utilities

### Binary File Structure Pattern

All Serato binary files follow this pattern:
1. Files consist of nested field entries
2. Each field has a 4-byte identifier (e.g., "vrsn", "otrk")
3. Fields can contain basic values (str/bytes/int/bool) or nested EntryLists
4. Version field ("vrsn") is always first
5. Data is typically big-endian encoded

Example entry structure:
```python
entries = [
    (Fields.VERSION, "1.0/Serato ScratchLive Crate"),
    (Fields.TRACK, [
        (Fields.TRACK_PATH, "Music/Artist/Track.mp3")
    ])
]
```

### Testing

Tests are in the `test/` directory using Python's unittest framework:
- Test data files are in `test/data/` and `data/` directories
- Each module has a corresponding test file (e.g., `test_crate.py` for `crate.py`)
- Tests validate parsing, modification, and serialization of binary files
- CI runs tests on Python 3.12 and 3.13 on Windows

### Key Patterns

**Modifying Entries**:
Use `modify_entries()` pattern with callback functions that receive the previous value and return the new value:
```python
def modify_color(prev_val):
    if prev_val == old_color:
        return new_color

tags.modify_entries({
    "cues": [{"field": "color", "func": modify_color}]
})
```

**Field Access**:
Always use the `Fields` enum to access field identifiers:
```python
db.Fields.FILE_PATH  # Use this
"pfil"  # Not this (though it's the same value)
```

**Serato File Locations**:
- Database: `Music/_Serato_/database V2`
- Crates: `Music/_Serato_/Subcrates/*.crate`
- Smart Crates: `Music/_Serato_/SmartCrates/*.scrate`

### Dependencies

**Core dependencies** (always installed):
- mutagen - Read/write audio file metadata and GEOB tags
- numpy - Beatgrid analysis
- librosa - Audio analysis
- pillow - Waveform image generation (Python < 3.14 uses any version, >= 3.14 requires v12+)

### Important Notes

- Always backup database files before modification
- `delete_tags_v1=True` is often required when modifying track tags for changes to appear in Serato
- Track paths in Serato files use forward slashes and are relative to the Music folder
- The project was originally forked from https://github.com/Holzhaus/serato-tags and https://github.com/sharst/seratopy
