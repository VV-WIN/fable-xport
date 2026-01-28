# Fable Book Exporter

CLI tool to export your Fable.co library via their API. Supports CSV, JSON, and Markdown output formats.

## Features

- Export to CSV (30+ columns), JSON (hierarchical), or Markdown (human-readable)
- Comprehensive data extraction: ratings (overall + 4 detailed dimensions), reviews, reading progress, metadata
- Per-list or combined export modes
- StoryGraph-compatible output
- Automatic pagination handling for large libraries
- JWT authentication with credential caching

## Installation

Clone the repo and run:

```bash
./run.bat    # Windows
./run.sh     # Mac/Linux
```

Uses `uv` to bootstrap Python environment and dependencies automatically.

## Configuration

On first run, you'll be prompted for two values:

**User ID:** UUID from any `api.fable.co` request URL  
**Auth Token:** JWT token from `Authorization` header (exclude the "JWT " prefix)

Extract these via browser DevTools (F12 → Network tab → inspect any Fable API call).

Credentials are stored locally in `.env`:

```
FABLE_USER_ID=your-uuid-here
FABLE_AUTH_TOKEN=your-jwt-token-here
```

## Usage

Run the launcher script and follow the interactive prompts:

1. Select output formats (CSV, JSON, MD)
2. Choose export mode (separate files per list vs single combined file)
3. Specify output directory (default: `./exports`)

Export runs automatically once confirmed.

## Output Formats

### CSV
Tabular format with 30+ columns:
- Book metadata: title, subtitle, authors, ISBN, publisher, pages, published date, cover URL
- Reading data: status, started/finished dates, current page
- Ratings: overall + characters/plot/writing/setting (1-5 scale)
- Review data: text, spoiler flag, DNF status, liked/disliked/disagreed summaries
- Categorization: genres, moods, content warnings, custom attributes
- Engagement: emoji reactions, spicy level

### JSON
Hierarchical structure with nested objects:
```json
{
  "title": "Book Title",
  "rating": 4.5,
  "detailed_ratings": {
    "characters": 4.0,
    "plot": 4.5,
    "writing_style": 5.0,
    "setting": 4.0
  },
  "genres": ["Fantasy", "Adventure"],
  "started_reading": "2025-01-20"
}
```

### Markdown
Human-readable format organized by reading status. Includes formatted ratings, metadata lists, and review text.

## API Implementation

Uses Fable's v2 REST API:
- `GET /api/v2/users/{user_id}/book_lists` - fetch list metadata
- `GET /api/v2/users/{user_id}/book_lists/{list_id}/books` - paginated book retrieval
- `GET /api/users/{user_id}/reviews/` - rating/review data (note: v1 endpoint)

Authentication: `Authorization: JWT {token}` header on all requests.

Data normalization handles nested book objects and merges review data by book ID.

## Troubleshooting

**403 Forbidden:** Token expired or malformed. Re-extract from browser and delete `.env`.

**Missing data:** Not all books have all fields. Rating dimensions only present if user rated them. Review data only present for reviewed books.

**Slow exports:** Expected for large libraries. ~1 min for 500 books. Progress shown per-list.

**NoneType errors:** Should be handled gracefully. If persist, check for data structure changes in Fable API responses.

## Technical Details

**Dependencies:** Python 3.7+, requests, python-dotenv  
**Architecture:** CLI orchestration layer, API client module, format-specific exporters  
**Error handling:** Graceful degradation - partial exports succeed even with some failures  
**Data flow:** Fetch lists → Fetch books per list → Fetch reviews → Merge by ID → Export

See `TROUBLESHOOTING.md` for common issues and detailed debugging steps.

## License

MIT

## Notes

Fable.co doesn't provide an official export feature. This tool reverse-engineers their API. May break if they change their endpoints or authentication scheme.

Credentials stored in plaintext in `.env`. Don't commit to version control. Add to `.gitignore` if forking.
