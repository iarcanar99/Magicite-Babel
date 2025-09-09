# Magicite Babel v9.5

<div align="center">

<img src="https://res.cloudinary.com/docoo51xb/image/upload/v1754806071/MBB_icon_oua6nq.png" alt="Magicite Babel" width="120">

**Real-time OCR Translation System for RPG Games**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-9.5-blue.svg)](https://github.com/iarcanar99/Magicite-Babel)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[Website](https://iarcanar99.github.io/magicite_babel/) • [Documentation](#-usage) • [Download](#-installation)

</div>

## Overview

Magicite Babel is an advanced real-time OCR translation system specifically designed for RPG games. It uses cutting-edge OCR and AI technology to translate in-game text from English to Thai in real-time, with special optimization for Final Fantasy XIV.

## Key Features

- 🔄 **Real-time Translation** - Instant text translation as it appears in games
- 🎯 **High-accuracy OCR** - Precise text detection with advanced image processing
- 🧠 **Smart Character Database** - Context-aware NPC and character management
- ⚡ **Performance Optimized** - Significant performance improvements over previous versions
- 🎮 **FFXIV Specialized** - Tailored features for Final Fantasy XIV gameplay

## Screenshots

<div align="center">
<table>
<tr>
<td align="center"><img src="https://res.cloudinary.com/docoo51xb/image/upload/v1754802395/MBBv9_mbb_znmona.png" width="250"><br><b>Main Interface</b></td>
<td align="center"><img src="https://res.cloudinary.com/docoo51xb/image/upload/v1754802396/MBBv9_control_ui_taju6v.png" width="250"><br><b>Control Panel</b></td>
</tr>
<tr>
<td align="center"><img src="https://res.cloudinary.com/docoo51xb/image/upload/v1754804053/MBBv9_TUI_pwryhd.png" width="250"><br><b>Translation Display</b></td>
<td align="center"><img src="https://res.cloudinary.com/docoo51xb/image/upload/v1754804334/MBBv9_NPC_manager_z34fd7.png" width="250"><br><b>NPC Manager</b></td>
</tr>
</table>
</div>

## What's New in v9.5

### 🧠 Advanced Choice Dialog Detection
- Smart Area Processing for FFXIV choice dialogs
- 15+ pattern recognition formats (numbered, bulleted lists)
- Enhanced OCR error tolerance and correction

### 🎛️ Enhanced Performance Control
- Full CPU limit options (50%, 60%, 80%, 100%)
- Advanced Settings UI improvements (450px layout)
- Real-time performance monitoring

### ✨ UI/UX Improvements
- Clean control interface design
- Bug fixes for AttributeError issues
- Optimized layout and spacing

## Installation

### System Requirements
- Windows 10/11
- Python 3.8+
- 4GB RAM (8GB recommended)

### Quick Start

1. **Clone and setup**
   ```bash
   git clone https://github.com/iarcanar99/Magicite-Babel.git
   cd Magicite-Babel
   pip install -r requirements.txt
   ```

2. **Launch**
   ```bash
   mbbv9.bat
   ```

3. **Configure**
   - Set translation areas (A, B)
   - Select game preset
   - Adjust CPU limit (Settings > Advanced)
   - Press F9 to start translating

## Usage

### Core Features
- **Real-time Translation**: English → Thai with AI context
- **OCR Processing**: High-accuracy text detection
- **Smart Caching**: 75-entry intelligent cache system
- **Character Database**: NPC context management
- **FFXIV Optimization**: Specialized for Final Fantasy XIV

### Keyboard Shortcuts
- `F9` - Start/Stop translation
- `F10` - Force translate
- `Alt+L` - Toggle UI
- `R-Click` - Force translate at cursor

### Dialog Types (FFXIV)
- ✅ **Normal Dialog**: Area A (speaker) + Area B (text)
- ✅ **Choice Dialog**: Area A (empty) + Area B (choices)
- ✅ **Lore Text**: Custom area configuration

## Configuration

### Basic Settings (`settings.json`)
```json
{
  "cpu_limit": 100,
  "cache_size": 75,
  "cache_ttl": 600,
  "translate_areas": {
    "A": {"start_x": 852, "start_y": 656, "end_x": 1114, "end_y": 700},
    "B": {"start_x": 838, "start_y": 700, "end_x": 1641, "end_y": 907}
  }
}
```

### Performance Tuning
- **CPU Usage**: Adjustable 50-100% in Advanced Settings
- **Cache Management**: Smart eviction based on usage frequency
- **OCR Processing**: Optimized for game text detection

## Troubleshooting

### Common Issues
- **Translation not working**: Check area settings, ensure windowed mode
- **Thai text not displaying**: Verify system Thai fonts, restart with `mbbv9.bat`
- **Low performance**: Increase CPU limit to 100%, enable GPU acceleration

### Logs
Debug information available in `logs/mbb_debug_YYYYMMDD_HHMMSS.log`

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/name`)
5. Open Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **Website**: [iarcanar99.github.io/magicite_babel](https://iarcanar99.github.io/magicite_babel/)
- **Issues**: [GitHub Issues](https://github.com/iarcanar99/Magicite-Babel/issues)

---

<div align="center">

**MBB v9.5 - Real-time translation for seamless gaming**

*Advanced OCR • AI Translation • FFXIV Optimized*

</div>
