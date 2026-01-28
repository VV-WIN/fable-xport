import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def normalize_book(book: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize book data from API response to standard format.
    Handles nested book objects and various field names.
    Extracts comprehensive metadata for StoryGraph compatibility.
    """
    # Handle None or invalid book objects
    if not book or not isinstance(book, dict):
        return {
            "title": "",
            "subtitle": "",
            "authors": [],
            "isbn": None,
            "imprint": None,
            "page_count": None,
            "published_date": None,
            "description": "",
            "cover_image": "",
            "genres": [],
            "storygraph_genres": [],
            "moods": [],
            "content_warnings": [],
            "status": None,
            "rating": None,
            "review": "",
            "review_summary_liked": "",
            "review_summary_disliked": "",
            "review_summary_disagreed": "",
            "contains_spoilers": None,
            "did_not_finish": None,
            "review_created_at": None,
            "added_at": None,
            "started_reading_at": "",
            "finished_reading_at": "",
            "current_page": None,
            "total_pages": None,
            "characters_rating": None,
            "plot_rating": None,
            "writing_style_rating": None,
            "setting_rating": None,
            "attributes": [],
            "emoji_reaction": "",
            "spicy_level": None,
        }
    
    # If book data is nested under 'book' key, extract it
    book_data = book.get("book", book) if isinstance(book.get("book"), dict) else book
    
    # Safely get authors
    authors = book_data.get("authors") or book.get("authors") or []
    if not isinstance(authors, list):
        authors = []
    
    # Extract genres
    genres = []
    if book_data.get("genres"):
        genres = [g.get("name") for g in book_data.get("genres", []) if isinstance(g, dict) and g.get("name")]
    
    # Extract StoryGraph tags (moods, content warnings)
    storygraph_tags = book_data.get("storygraph_tags") or {}
    moods = storygraph_tags.get("moods", []) if isinstance(storygraph_tags, dict) else []
    content_warnings = storygraph_tags.get("content_warnings", []) if isinstance(storygraph_tags, dict) else []
    storygraph_genres = storygraph_tags.get("genres", []) if isinstance(storygraph_tags, dict) else []
    
    # Extract review summary
    review_summary = book_data.get("review_summary") or {}
    liked = review_summary.get("liked") if isinstance(review_summary, dict) else ""
    disliked = review_summary.get("disliked") if isinstance(review_summary, dict) else ""
    disagreed = review_summary.get("disagreed") if isinstance(review_summary, dict) else ""
    
    # Extract reading progress
    reading_progress = book_data.get("reading_progress") or {}
    read_status = reading_progress.get("status") if isinstance(reading_progress, dict) else ""
    current_page = reading_progress.get("current_page")
    total_pages = reading_progress.get("page_count")
    
    # Extract detailed ratings (from review if available)
    characters_rating = book.get("characters_rating")
    plot_rating = book.get("plot_rating")
    writing_style_rating = book.get("writing_style_rating")
    setting_rating = book.get("setting_rating")
    
    # Extract attributes/labels
    attributes = book.get("attributes", []) or []
    if not isinstance(attributes, list):
        attributes = []
    attribute_names = [a.get("name") for a in attributes if isinstance(a, dict) and a.get("name")]
    
    # Extract cover image URL
    cover_image = book_data.get("cover_image") or ""
    
    return {
        "title": book_data.get("title") or book.get("title"),
        "subtitle": book_data.get("subtitle") or "",
        "authors": authors,
        "isbn": book_data.get("isbn") or book.get("isbn"),
        "imprint": book_data.get("publisher") or book_data.get("imprint") or book.get("publisher"),
        "page_count": book_data.get("page_count") or book_data.get("pages") or book.get("page_count"),
        "published_date": book_data.get("published_date") or book_data.get("publish_date") or book.get("published_date"),
        "description": book_data.get("description") or "",
        "cover_image": cover_image,
        "genres": genres,
        "storygraph_genres": storygraph_genres,
        "moods": moods,
        "content_warnings": content_warnings,
        "status": read_status or book.get("status"),
        "rating": book.get("rating"),
        "review": book.get("review") or "",
        "review_summary_liked": liked,
        "review_summary_disliked": disliked,
        "review_summary_disagreed": disagreed,
        "contains_spoilers": book.get("contains_spoilers"),
        "did_not_finish": book.get("did_not_finish"),
        "review_created_at": book.get("review_created_at") or book.get("created_at"),
        "added_at": book.get("added_at"),
        "started_reading_at": book_data.get("started_reading_at") or "",
        "finished_reading_at": book_data.get("finished_reading_at") or "",
        "current_page": current_page,
        "total_pages": total_pages,
        "characters_rating": characters_rating,
        "plot_rating": plot_rating,
        "writing_style_rating": writing_style_rating,
        "setting_rating": setting_rating,
        "attributes": attribute_names,
        "emoji_reaction": book.get("emoji_reaction") or (book.get("emoji") or {}).get("content") or "",
        "spicy_level": book.get("spicy_level"),
    }


def format_author_name(name: str) -> str:
    """Format author name for display."""
    return name.strip() if name else ""


def format_authors_list(authors: List[Any]) -> str:
    """Convert authors list to comma-separated string."""
    if not authors or not isinstance(authors, list):
        return ""

    author_names = []
    for author in authors:
        if isinstance(author, dict):
            name = author.get("name", "")
        elif isinstance(author, str):
            name = author
        else:
            name = ""

        if name:
            author_names.append(name)

    return ", ".join(author_names)


def extract_isbn(isbn: Optional[str]) -> tuple[str, str]:
    """Split ISBN into ISBN-10 and ISBN-13."""
    if not isbn:
        return "", ""

    normalized = isbn.replace("-", "")

    if len(normalized) == 10:
        return normalized, ""
    if len(normalized) == 13:
        return "", normalized

    return normalized, ""


def format_date(date_str: Optional[str]) -> str:
    """Convert ISO date to readable format."""
    if not date_str:
        return ""

    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except (ValueError, AttributeError):
        return ""


def export_to_csv(books: List[Dict[str, Any]], output_path: Path) -> Path:
    """
    Export books to CSV format with comprehensive metadata for StoryGraph.

    Args:
        books: List of book dictionaries
        output_path: Path to write CSV file

    Returns:
        Path to created CSV file
    """
    if not books:
        raise ValueError("No books to export")

    fieldnames = [
        "Title",
        "Subtitle",
        "Author(s)",
        "ISBN-10",
        "ISBN-13",
        "Publisher",
        "Pages",
        "Published Date",
        "Genres",
        "Moods",
        "Content Warnings",
        "Status",
        "Rating",
        "Characters Rating",
        "Plot Rating",
        "Writing Style Rating",
        "Setting Rating",
        "Review",
        "Review Summary - Liked",
        "Review Summary - Disliked",
        "Review Summary - Disagreed",
        "Attributes/Tags",
        "Emoji Reaction",
        "Contains Spoilers",
        "Did Not Finish",
        "Started Reading",
        "Finished Reading",
        "Date Added",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for book in books:
            if book is None:
                continue
            book = normalize_book(book)
            isbn10, isbn13 = extract_isbn(book.get("isbn"))
            authors = book.get("authors", [])

            row = {
                "Title": book.get("title", ""),
                "Subtitle": book.get("subtitle", ""),
                "Author(s)": format_authors_list(authors),
                "ISBN-10": isbn10,
                "ISBN-13": isbn13,
                "Publisher": book.get("imprint", ""),
                "Pages": book.get("page_count", ""),
                "Published Date": format_date(book.get("published_date")),
                "Genres": "; ".join(book.get("genres", [])),
                "Moods": "; ".join(book.get("moods", [])),
                "Content Warnings": "; ".join(book.get("content_warnings", [])),
                "Status": book.get("status", ""),
                "Rating": book.get("rating", ""),
                "Characters Rating": book.get("characters_rating", ""),
                "Plot Rating": book.get("plot_rating", ""),
                "Writing Style Rating": book.get("writing_style_rating", ""),
                "Setting Rating": book.get("setting_rating", ""),
                "Review": book.get("review", ""),
                "Review Summary - Liked": book.get("review_summary_liked", ""),
                "Review Summary - Disliked": book.get("review_summary_disliked", ""),
                "Review Summary - Disagreed": book.get("review_summary_disagreed", ""),
                "Attributes/Tags": "; ".join(book.get("attributes", [])),
                "Emoji Reaction": book.get("emoji_reaction", ""),
                "Contains Spoilers": "Yes" if book.get("contains_spoilers") else "No",
                "Did Not Finish": "Yes" if book.get("did_not_finish") else "No",
                "Started Reading": format_date(book.get("started_reading_at")),
                "Finished Reading": format_date(book.get("finished_reading_at")),
                "Date Added": format_date(
                    book.get("review_created_at")
                    or book.get("added_at")
                    or book.get("created_at")
                ),
            }

            writer.writerow(row)

    return output_path

    return output_path


def export_to_json(books: List[Dict[str, Any]], output_path: Path) -> Path:
    """
    Export books to JSON format with comprehensive metadata for StoryGraph.

    Args:
        books: List of book dictionaries
        output_path: Path to write JSON file

    Returns:
        Path to created JSON file
    """
    if not books:
        raise ValueError("No books to export")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Clean up books for JSON export
    clean_books = []
    for book in books:
        if book is None:
            continue
        book = normalize_book(book)
        isbn10, isbn13 = extract_isbn(book.get("isbn"))
        authors = book.get("authors", [])

        clean_book = {
            "title": book.get("title"),
            "subtitle": book.get("subtitle"),
            "authors": format_authors_list(authors),
            "isbn10": isbn10,
            "isbn13": isbn13,
            "publisher": book.get("imprint"),
            "pages": book.get("page_count"),
            "published_date": format_date(book.get("published_date")),
            "description": book.get("description"),
            "cover_image": book.get("cover_image"),
            "genres": book.get("genres"),
            "moods": book.get("moods"),
            "content_warnings": book.get("content_warnings"),
            "status": book.get("status"),
            "rating": float(book.get("rating")) if book.get("rating") else None,
            "detailed_ratings": {
                "characters": float(book.get("characters_rating")) if book.get("characters_rating") else None,
                "plot": float(book.get("plot_rating")) if book.get("plot_rating") else None,
                "writing_style": float(book.get("writing_style_rating")) if book.get("writing_style_rating") else None,
                "setting": float(book.get("setting_rating")) if book.get("setting_rating") else None,
            },
            "review": book.get("review"),
            "review_summary": {
                "liked": book.get("review_summary_liked"),
                "disliked": book.get("review_summary_disliked"),
                "disagreed": book.get("review_summary_disagreed"),
            },
            "contains_spoilers": book.get("contains_spoilers"),
            "did_not_finish": book.get("did_not_finish"),
            "attributes": book.get("attributes"),
            "emoji_reaction": book.get("emoji_reaction"),
            "spicy_level": book.get("spicy_level"),
            "started_reading": format_date(book.get("started_reading_at")),
            "finished_reading": format_date(book.get("finished_reading_at")),
            "current_page": book.get("current_page"),
            "total_pages": book.get("total_pages"),
            "date_added": format_date(
                book.get("review_created_at")
                or book.get("added_at")
                or book.get("created_at")
            ),
        }
        clean_books.append(clean_book)

    with open(output_path, "w", encoding="utf-8") as jsonfile:
        json.dump(
            clean_books, jsonfile, indent=2, ensure_ascii=False, default=str
        )

    return output_path


def export_to_markdown(books: List[Dict[str, Any]], output_path: Path) -> Path:
    """
    Export books to Markdown format with comprehensive metadata for StoryGraph.

    Args:
        books: List of book dictionaries
        output_path: Path to write Markdown file

    Returns:
        Path to created Markdown file
    """
    if not books:
        raise ValueError("No books to export")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# My Fable Book Library\n",
        f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"Total books: {len(books)}\n",
        "\n---\n",
    ]

    # Group by status
    by_status = {}
    for book in books:
        if book is None:
            continue
        book = normalize_book(book)
        status = book.get("status", "unknown")
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(book)

    status_order = ["finished", "reading", "unread"]
    status_labels = {
        "finished": "Finished",
        "reading": "Currently Reading",
        "unread": "Want to Read",
    }

    for status in status_order:
        if status in by_status:
            status_title = status_labels.get(status, status.title())
            lines.append(f"\n## {status_title} ({len(by_status[status])})\n")

            for book in by_status[status]:
                title = book.get("title", "Unknown")
                subtitle = book.get("subtitle", "")
                authors = format_authors_list(book.get("authors", []))
                rating = book.get("rating")
                review = book.get("review")
                genres = book.get("genres", [])
                moods = book.get("moods", [])
                attributes = book.get("attributes", [])
                started = format_date(book.get("started_reading_at"))
                finished = format_date(book.get("finished_reading_at"))
                emoji = book.get("emoji_reaction", "")
                
                # Detailed ratings
                char_rating = book.get("characters_rating")
                plot_rating = book.get("plot_rating")
                writing_rating = book.get("writing_style_rating")
                setting_rating = book.get("setting_rating")

                lines.append(f"### {title}\n")
                
                if subtitle:
                    lines.append(f"*{subtitle}*\n\n")
                
                if authors:
                    lines.append(f"**Author(s):** {authors}\n")

                if rating:
                    emoji_str = f" {emoji}" if emoji else ""
                    lines.append(f"**Rating:** {rating}/5{emoji_str}\n")
                
                # Detailed ratings
                has_detailed_ratings = any([char_rating, plot_rating, writing_rating, setting_rating])
                if has_detailed_ratings:
                    lines.append(f"**Detailed Ratings:**\n")
                    if char_rating:
                        lines.append(f"- Characters: {char_rating}/5\n")
                    if plot_rating:
                        lines.append(f"- Plot: {plot_rating}/5\n")
                    if writing_rating:
                        lines.append(f"- Writing Style: {writing_rating}/5\n")
                    if setting_rating:
                        lines.append(f"- Setting: {setting_rating}/5\n")
                
                if genres:
                    lines.append(f"**Genres:** {', '.join(genres)}\n")
                
                if moods:
                    lines.append(f"**Moods:** {', '.join(moods)}\n")
                
                if attributes:
                    lines.append(f"**Tags:** {', '.join(attributes)}\n")

                if started or finished:
                    lines.append(f"**Read Dates:** ")
                    if started:
                        lines.append(f"Started {started}")
                    if finished:
                        if started:
                            lines.append(f" → Finished {finished}")
                        else:
                            lines.append(f"Finished {finished}")
                    lines.append("\n")

                if review:
                    lines.append(f"\n**Review:**\n\n{review}\n")

                lines.append("\n---\n")

    with open(output_path, "w", encoding="utf-8") as mdfile:
        mdfile.writelines(lines)

    return output_path
