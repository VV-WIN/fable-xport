import sys
from pathlib import Path
from typing import Optional

from fable_api import FableAPIError, fetch_all_books, fetch_user_reviews, merge_reviews_with_books
from exporters import export_to_csv, export_to_json, export_to_markdown


def print_header() -> None:
    """Print welcome header."""
    print("\n" + "=" * 60)
    print("  FABLE BOOK EXPORTER")
    print("  Free your books from Fable!")
    print("=" * 60 + "\n")


def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{title}")
    print("-" * len(title))


def ask_yes_no(prompt: str) -> bool:
    """Ask user a yes/no question."""
    while True:
        response = input(f"\n{prompt} (yes/no): ").strip().lower()
        if response in ("yes", "y"):
            return True
        elif response in ("no", "n"):
            return False
        else:
            print("Please enter 'yes' or 'no'")


def ask_choice(prompt: str, choices: list[tuple[str, str]]) -> str:
    """Ask user to choose from options."""
    print(f"\n{prompt}")
    for i, (key, label) in enumerate(choices, 1):
        print(f"  {i}. {label}")

    while True:
        try:
            choice = input("\nEnter your choice (1-{}): ".format(len(choices))).strip()
            idx = int(choice) - 1
            if 0 <= idx < len(choices):
                return choices[idx][0]
        except ValueError:
            pass

        print(f"Please enter a number between 1 and {len(choices)}")


def setup_env_file() -> bool:
    """Guide user through setting up .env file if not already done."""
    env_path = Path(".env")

    if env_path.exists():
        return True

    print_section("First Time Setup")
    print(
        "I need to set up your Fable credentials to access your books.\n"
        "Follow these steps to find your credentials:"
    )

    print("\n=== Step 1: Get Your User ID ===")
    print("1. Open Fable in your web browser (fable.com)")
    print("2. Open Developer Tools (F12 or right-click → Inspect)")
    print("3. Go to the Network tab")
    print("4. Refresh the page")
    print("5. Look for requests to 'api.fable.co'")
    print("6. In the request URL, find the USER_ID (it's a UUID)")
    print("   Example: https://api.fable.co/api/v2/users/21321312312/")
    print("           The USER_ID is: 21321312312\n")

    user_id = input("Enter your FABLE_USER_ID: ").strip()

    if not user_id:
        print("Error: User ID is required!")
        return False

    print("\n=== Step 2: Get Your Auth Token ===")
    print("In the same Developer Tools:")
    print("1. Click on any request to 'api.fable.co'")
    print("2. Look at the 'Request Headers' section")
    print("3. Find the 'Authorization' header")
    print("4. Copy ONLY the token value (everything after 'Token ')")
    print("   Example: If you see 'Authorization: Token abc123def456...'")
    print("            Copy only: abc123def456...")
    print("\n   OR find 'Cookie' header and look for 'token=' or 'auth_token='")
    print("   Example: Cookie: token=xyz789; other=value")
    print("            Copy only: xyz789\n")

    auth_token = input("Enter your FABLE_AUTH_TOKEN: ").strip()

    if not auth_token:
        print("Error: Auth token is required!")
        return False

    # Create .env file
    content = f"""# Fable Credentials
FABLE_USER_ID={user_id}
FABLE_AUTH_TOKEN={auth_token}
"""

    env_path.write_text(content)
    print(f"\n✓ Configuration saved to {env_path}")

    return True


def select_export_formats() -> list[str]:
    """Ask user which formats to export."""
    print_section("Export Formats")
    print("Which format(s) would you like to export? (You can choose multiple)")

    formats = []
    choices = [
        ("csv", "CSV (spreadsheet - import to Excel, Google Sheets)"),
        ("json", "JSON (structured data format)"),
        ("md", "Markdown (readable text format)"),
    ]

    for key, label in choices:
        if ask_yes_no(f"Export as {label}?"):
            formats.append(key)

    if not formats:
        print("\nNo formats selected. Using CSV (default).")
        return ["csv"]

    return formats


def ask_separate_lists() -> bool:
    """Ask if user wants separate files for each list."""
    print_section("Export Options")
    return ask_yes_no(
        "Do you want to export each book list to a separate file?\n"
        "(Yes = separate files per list, No = one combined file)"
    )


def get_output_directory() -> Path:
    """Ask user where to save exports."""
    print_section("Output Location")
    print("Where would you like to save your exported books?")
    print("(Press Enter to use: ./exports)\n")

    default = Path("exports")
    user_input = input("Enter path: ").strip()

    if not user_input:
        print(f"Using default: {default}")
        return default

    return Path(user_input)


def export_books(output_dir: Path, formats: list[str], separate_lists: bool = False) -> None:
    """Fetch and export books in selected formats."""
    print_section("Exporting Your Books")

    print("Connecting to Fable...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch reviews to merge with book data
    print("Fetching your reviews and ratings...")
    reviews = fetch_user_reviews()
    if reviews:
        print(f"✓ Found {len(reviews)} reviews with ratings!\n")
    else:
        print("⊘ No reviews found (this is okay, will export with available data)\n")

    if separate_lists:
        # Export each list separately
        try:
            from fable_api import fetch_user_lists, fetch_books_from_list
            lists = fetch_user_lists()
            print(f"✓ Found {len(lists)} book lists!\n")

            total_books = 0
            for book_list in lists:
                list_id = book_list.get("id")
                list_name = book_list.get("name", "Unknown")
                count = book_list.get("count", 0)
                
                print(f"Fetching '{list_name}' ({count} books)...")
                
                try:
                    books = fetch_books_from_list(list_id)
                    # Filter out None books and books without proper structure
                    books = [b for b in books if b is not None and isinstance(b, dict)]
                    # Merge reviews into books
                    books = merge_reviews_with_books(books, reviews)
                    
                    if books:
                        # Sanitize filename
                        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in list_name)
                        safe_name = safe_name.replace(' ', '_')
                        
                        exported_formats = []
                        for fmt in formats:
                            try:
                                if fmt == "csv":
                                    path = output_dir / f"{safe_name}.csv"
                                    export_to_csv(books, path)
                                    exported_formats.append("CSV")
                                elif fmt == "json":
                                    path = output_dir / f"{safe_name}.json"
                                    export_to_json(books, path)
                                    exported_formats.append("JSON")
                                elif fmt == "md":
                                    path = output_dir / f"{safe_name}.md"
                                    export_to_markdown(books, path)
                                    exported_formats.append("MD")
                            except Exception as export_error:
                                print(f"  ✗ Error exporting {fmt} for '{list_name}': {export_error}")
                                continue
                        
                        formats_str = ", ".join(exported_formats)
                        print(f"  ✓ Exported {len(books)} books from '{list_name}' ({formats_str})")
                        total_books += len(books)
                    else:
                        print(f"  ⊘ List '{list_name}' is empty")
                except Exception as e:
                    print(f"  ✗ Error: {e}")
            
            print(f"\n✓ Total: {total_books} books exported")
            
        except FableAPIError as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)
    else:
        # Export all books combined
        try:
            books = fetch_all_books()
            # Filter out None books
            books = [b for b in books if b is not None]
            # Merge reviews into books
            books = merge_reviews_with_books(books, reviews)
        except FableAPIError as e:
            print(f"\n✗ Error: {e}")
            sys.exit(1)

        print(f"✓ Found {len(books)} books!")

        if not books:
            print("No books to export.")
            return

        for fmt in formats:
            try:
                if fmt == "csv":
                    path = output_dir / "fable_books.csv"
                    export_to_csv(books, path)
                    print(f"✓ Exported to {path}")

                elif fmt == "json":
                    path = output_dir / "fable_books.json"
                    export_to_json(books, path)
                    print(f"✓ Exported to {path}")

                elif fmt == "md":
                    path = output_dir / "fable_books.md"
                    export_to_markdown(books, path)
                    print(f"✓ Exported to {path}")

            except Exception as e:
                print(f"✗ Error exporting {fmt}: {e}")

    print_section("Export Complete!")
    print(f"Your books have been saved to: {output_dir.absolute()}")


def main() -> None:
    """Main CLI entry point."""
    print_header()

    # Check for .env file
    if not setup_env_file():
        print("\n✗ Setup failed. Please create a .env file with your credentials.")
        sys.exit(1)

    # Ask user preferences
    formats = select_export_formats()
    separate_lists = ask_separate_lists()
    output_dir = get_output_directory()

    # Confirm before exporting
    print("\n" + "=" * 60)
    print(f"Formats to export: {', '.join(formats).upper()}")
    print(f"Export mode: {'Separate file per list' if separate_lists else 'Combined file'}")
    print(f"Output directory: {output_dir.absolute()}")
    print("=" * 60)

    if not ask_yes_no("Proceed with export?"):
        print("Export cancelled.")
        sys.exit(0)

    # Export
    export_books(output_dir, formats, separate_lists)


if __name__ == "__main__":
    main()
