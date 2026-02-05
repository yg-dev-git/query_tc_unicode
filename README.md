# Query TC Unicode

A Python tool to query attributes and meanings for Traditional Chinese characters (and Unicode numbers) using CNS11643 and Zdic.

## Features

- **Character Attributes**: Fetch CNS code, IDS (Ideographic Description Sequence), Components, and Stroke Order from [CNS11643](https://www.cns11643.gov.tw/).
- **Character Meaning**: Fetch basic definitions and explanations from [Zdic (漢典)](https://www.zdic.net/).
- **Unicode Support**: Supports querying by character (e.g., `數`) or by Unicode hexadecimal string (e.g., `2A838`).
- **Browser Automation**: Uses [Pydoll](https://github.com/m-v-p-s/pydoll) for robust scraping of JavaScript-rendered content.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)
- A Chromium-based browser (Chrome or Chromium) installed on your system.

## Installation

```bash
git clone https://github.com/yg-dev-git/query_tc_unicode.git
cd query_tc_unicode
uv sync
```

## Usage

### Simple Example

```python
import asyncio
from query_tc_unicode import get_character_attributes, get_character_meaning

async def main():
    # Get attributes
    attrs = await get_character_attributes("數")
    print(f"CNS: {attrs['cns']}")
    print(f"IDS: {attrs['ids']}")
    
    # Get meaning
    meaning = await get_character_meaning("舡")
    print(f"Meaning: {meaning}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Included Test Script

```bash
uv run main.py
```

## Data Sources

- **CNS11643**: For character properties and stroke information.
- **Zdic (漢典)**: For definitions and dictionary data.
