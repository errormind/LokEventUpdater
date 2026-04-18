# LokEventUpdater

A tool to collect and manage events from "LOK Kulturzentrum Jever" and sync them across various platforms.

## Overview

This project crawls event data from the LOK Kulturzentrum website and stores it locally for easier access and distribution to other platforms. It fetches event information including dates, times, locations, prices, and ticket URLs.

## Features

- ✅ Crawls events from the LOK Kulturzentrum website
- ✅ Stores event data as JSON for easy access
- 🚧 Planned: Web UI for managing event updates
- 🚧 Planned: Sync events to multiple platforms

## Installation

### Prerequisites

- Python 3.8+
- Windows (the project uses `.bat` scripts)

### Setup

1. Clone or download the repository
2. Run the setup script:
   ```
   setup.bat
   ```
   This will create a virtual environment and install dependencies.

## Usage

Run the event crawler:
```
run.bat
```

This will:
1. Activate the virtual environment
2. Run the crawler script
3. Fetch events from the LOK website
4. Save data to `data/events.json`

### Manual Execution

You can also run the crawler directly from Python:
```
python scripts/main.py
```

## Project Structure

```
LokEventUpdater/
├── scripts/
│   ├── CollectData.py      # Main crawler implementation
│   ├── main.py             # Entry point
│   └── html/               # HTML utilities
├── data/                   # Output directory for events and debug files
├── run.bat                 # Run the crawler
├── setup.bat               # Initial setup script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Data Collection

The crawler fetches events from the LOK Kulturzentrum's async API endpoint:
- **Endpoint**: `https://www.lok-jever.de/gutesio/operator/showcase_child_list_data/{offset}`
- **Module ID**: 70
- **Pagination**: 30 events per page

Each event includes:
- Event name/title
- Date and time
- Location
- Price
- Event type/category
- Ticket URLs
- Event description
- Venue information

## Output

Events are saved to `data/events.json` with the following structure:
```json
{
  "title": "Event Name",
  "date": "18.04.2026",
  "time": "19:00 - 23:00 Uhr",
  "location": "LOK Kulturzentrum",
  "type": "Musik & Konzerte",
  "price": "12,00 €",
  "url": "https://www.lok-jever.de/programm/event/...",
  "ticket_url": "https://nordsee.tickets/...",
  "fetched_at": "2026-04-18T13:03:34.586411"
}
```

## Dependencies

- `requests` - HTTP library for fetching data from the website

See `requirements.txt` for the complete list.

## Development

To work on the project:

1. Activate the virtual environment:
   ```
   venv\Scripts\activate.bat
   ```

2. Install development tools (if needed):
   ```
   pip install -r requirements.txt
   ```

3. Run tests or the crawler:
   ```
   python scripts/CollectData.py
   ```

## Troubleshooting

**Error: Virtual environment not found**
- Run `setup.bat` first to create the virtual environment

**Error: Module not found**
- Make sure the virtual environment is activated and dependencies are installed:
  ```
  venv\Scripts\activate.bat
  pip install -r requirements.txt
  ```

**No events found**
- The website may be down or have changed its API structure
- Check that you can access: `https://www.lok-jever.de/programm`

## License

This project is created for the LOK Kulturzentrum Jever.

---

Keep on rockin! 🎸
