import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


class FableAPIError(Exception):
    """Raised when Fable API requests fail."""

    pass


def validate_credentials() -> None:
    """Validate that required credentials are set."""
    load_dotenv()  # Reload environment variables
    user_id = os.getenv("FABLE_USER_ID")
    auth_token = os.getenv("FABLE_AUTH_TOKEN")
    
    if not user_id:
        raise FableAPIError(
            "FABLE_USER_ID is not set. Please configure your Fable credentials."
        )
    if not auth_token:
        raise FableAPIError(
            "FABLE_AUTH_TOKEN is not set. Please add your authentication token to .env file."
        )


def get_headers() -> Dict[str, str]:
    """Get authentication headers for API requests."""
    load_dotenv()  # Reload to get latest token
    auth_token = os.getenv("FABLE_AUTH_TOKEN")
    
    # Try to detect if user included prefix and remove it
    if auth_token:
        if auth_token.startswith("JWT "):
            auth_token = auth_token[4:]
        elif auth_token.startswith("Token "):
            auth_token = auth_token[6:]
        elif auth_token.startswith("Bearer "):
            auth_token = auth_token[7:]
    
    return {
        "Authorization": f"JWT {auth_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://fable.co/",
        "Origin": "https://fable.co"
    }


def get_user_id() -> str:
    """Get the user ID from environment."""
    load_dotenv()
    user_id = os.getenv("FABLE_USER_ID")
    if not user_id:
        raise FableAPIError("FABLE_USER_ID is not set.")
    return user_id


def fetch_owned_books() -> List[Dict[str, Any]]:
    """
    Fetch all owned/read books from Fable.

    Returns:
        List of book dictionaries with metadata
    """
    validate_credentials()

    all_books: List[Dict[str, Any]] = []
    url = "https://api.fable.co/api/v2/books/owned/?include=preorder,owned"

    while url:
        try:
            response = requests.get(url, headers=get_headers(), timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise FableAPIError(f"Failed to fetch owned books: {e}")

        data = response.json()

        # Handle both dict with results and direct list responses
        if isinstance(data, list):
            all_books.extend(data)
            break
        elif isinstance(data, dict):
            results = data.get("results", [])
            if isinstance(results, list):
                all_books.extend(results)
        else:
            raise FableAPIError("Unexpected response format from Fable API")

        url = data.get("next") if isinstance(data, dict) else None

    return all_books


def fetch_user_lists() -> List[Dict[str, Any]]:
    """
    Fetch all user book lists (system and custom).

    Returns:
        List of book list dictionaries with metadata
    """
    validate_credentials()
    user_id = get_user_id()

    try:
        url = f"https://api.fable.co/api/v2/users/{user_id}/book_lists"
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise FableAPIError(f"Failed to fetch book lists: {e}")

    data = response.json()
    
    # Handle both dict with results and direct list responses
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get("results", [])
    else:
        raise FableAPIError("Unexpected response format from Fable API")


def fetch_books_from_list(list_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all books from a specific list.

    Args:
        list_id: The ID of the book list

    Returns:
        List of books in the list
    """
    validate_credentials()
    user_id = get_user_id()

    all_books: List[Dict[str, Any]] = []
    offset = 0
    limit = 100

    while True:
        url = (
            f"https://api.fable.co/api/v2/users/{user_id}/book_lists/{list_id}/books"
            f"?offset={offset}&limit={limit}"
        )

        try:
            response = requests.get(url, headers=get_headers(), timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise FableAPIError(f"Failed to fetch books from list {list_id}: {e}")

        data = response.json()

        # Handle both dict with results and direct list responses
        if isinstance(data, list):
            all_books.extend(data)
            break
        elif isinstance(data, dict):
            results = data.get("results", [])
            if isinstance(results, list):
                all_books.extend(results)
        else:
            raise FableAPIError("Unexpected response format from Fable API")

        if not results or len(results) < limit:
            break

        offset += limit

    return all_books


def fetch_all_books() -> List[Dict[str, Any]]:
    """
    Fetch all books from all lists and owned books.

    Returns:
        Combined list of all books
    """
    all_books: List[Dict[str, Any]] = []

    # Get owned/read books
    try:
        owned = fetch_owned_books()
        all_books.extend(owned)
    except FableAPIError as e:
        print(f"Warning: Could not fetch owned books: {e}")

    # Get all lists and their books
    try:
        lists = fetch_user_lists()
        for book_list in lists:
            list_id = book_list.get("id")
            if list_id:
                try:
                    books = fetch_books_from_list(list_id)
                    all_books.extend(books)
                except FableAPIError as e:
                    print(f"Warning: Could not fetch books from list {list_id}: {e}")
    except FableAPIError as e:
        print(f"Warning: Could not fetch user lists: {e}")

    return all_books


def fetch_user_reviews() -> Dict[str, Dict[str, Any]]:
    """
    Fetch all user reviews with ratings and metadata.

    Returns:
        Dictionary mapping book IDs to review data
    """
    validate_credentials()
    user_id = get_user_id()

    reviews_by_book: Dict[str, Dict[str, Any]] = {}
    offset = 0
    limit = 20

    while True:
        # Try v2 endpoint first, fall back to v1 if needed
        url = f"https://api.fable.co/api/v2/users/{user_id}/reviews/?limit={limit}&offset={offset}"

        try:
            response = requests.get(url, headers=get_headers(), timeout=10)
            
            # If v2 endpoint doesn't exist, it might 404 - that's okay
            if response.status_code == 404:
                # Try v1 endpoint
                url = f"https://api.fable.co/api/users/{user_id}/reviews/?limit={limit}&offset={offset}"
                response = requests.get(url, headers=get_headers(), timeout=10)
            
            response.raise_for_status()
        except requests.RequestException as e:
            # Silently return empty reviews - this is not critical
            return reviews_by_book

        data = response.json()

        if not isinstance(data, dict):
            return reviews_by_book

        results = data.get("results", [])
        if not isinstance(results, list) or len(results) == 0:
            break

        for review in results:
            book_data = review.get("book", {})
            book_id = book_data.get("id")
            
            if book_id:
                reviews_by_book[book_id] = {
                    "rating": review.get("rating"),
                    "review": review.get("review"),
                    "contains_spoilers": review.get("contains_spoilers"),
                    "did_not_finish": review.get("did_not_finish"),
                    "characters_rating": review.get("characters_rating"),
                    "plot_rating": review.get("plot_rating"),
                    "writing_style_rating": review.get("writing_style_rating"),
                    "setting_rating": review.get("setting_rating"),
                    "attributes": review.get("attributes", []),
                    "emoji_reaction": review.get("emoji_reaction"),
                    "emoji": review.get("emoji"),
                    "spicy_level": review.get("spicy_level"),
                    "created_at": review.get("created_at"),
                    "updated_at": review.get("updated_at"),
                }

        if len(results) < limit:
            break

        offset += limit

    return reviews_by_book


def merge_reviews_with_books(books: List[Dict[str, Any]], reviews: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge review data into book objects.

    Args:
        books: List of book dictionaries
        reviews: Dictionary of reviews by book ID

    Returns:
        Books with merged review data
    """
    merged_books = []
    
    for book in books:
        # Skip None books
        if book is None or not isinstance(book, dict):
            continue
        
        try:
            # Get the actual book object if nested
            book_data = book.get("book", {}) if isinstance(book.get("book"), dict) else book
            
            # Handle case where book_data is None
            if not book_data or not isinstance(book_data, dict):
                merged_books.append(book)
                continue
            
            book_id = book_data.get("id")
            
            # Create merged object starting with original book data
            merged_book = dict(book)
            
            # Add review data if available
            if book_id and book_id in reviews:
                review_data = reviews[book_id]
                if review_data and isinstance(review_data, dict):
                    merged_book.update(review_data)
            
            merged_books.append(merged_book)
        except Exception:
            # If merge fails for this book, just add the original
            merged_books.append(book)
    
    return merged_books
