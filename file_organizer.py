import csv
import argparse
from pathlib import Path
from collections import defaultdict
import sys

def get_all_files(root_path: Path):
    """
    Get all files in the directory recursively, excluding temporary files (starting with ~$).
    """
    return [p for p in root_path.rglob('*') if p.is_file() and not p.name.startswith('~$')]

def resolve_duplicates(root_path: Path, dry_run: bool = False):
    """
    Renames files to ensure every file in the directory tree has a unique stem (filename without extension).
    """
    files = get_all_files(root_path)

    # Map stem -> list of files
    stem_map = defaultdict(list)
    for p in files:
        stem_map[p.stem].append(p)

    # Set of currently used stems to avoid collisions
    used_stems = set(stem_map.keys())

    duplicates = {k: v for k, v in stem_map.items() if len(v) > 1}
    renamed_count = 0

    print(f"Found {len(duplicates)} duplicate stems.")

    for stem, paths in duplicates.items():
        # Sort paths to ensure deterministic behavior (e.g., by string representation)
        paths.sort(key=lambda p: str(p))

        # Keep the first file as is.
        # Rename the rest.
        for p in paths[1:]:
            counter = 1
            while True:
                new_stem = f"{stem}({counter})"
                if new_stem not in used_stems:
                    # Found a unique stem
                    used_stems.add(new_stem)
                    break
                counter += 1

            new_name = f"{new_stem}{p.suffix}"
            new_path = p.parent / new_name

            if dry_run:
                print(f"[Dry Run] Rename: {p} -> {new_path}")
            else:
                try:
                    p.rename(new_path)
                    print(f"Renamed: {p} -> {new_path}")
                except OSError as e:
                    print(f"Error renaming {p}: {e}")

            renamed_count += 1

    return renamed_count

def generate_csv(root_path: Path, output_csv: Path):
    """
    Generates a CSV report of all files in the directory.
    """
    files = get_all_files(root_path)
    fieldnames = ['Absolute Path', 'Filename', 'Extension']

    try:
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in files:
                writer.writerow({
                    'Absolute Path': str(p.absolute()),
                    'Filename': p.stem,
                    'Extension': p.suffix
                })
        print(f"Report generated at: {output_csv}")
    except IOError as e:
        print(f"Error writing CSV: {e}")

def main():
    parser = argparse.ArgumentParser(description="Recursively rename duplicate files to ensure unique filenames.")
    parser.add_argument("directory", nargs='?', help="Target directory path")
    parser.add_argument("--dry-run", action="store_true", help="Simulate the renaming process without making changes")
    parser.add_argument("--csv", help="Custom path for the CSV report", default=None)

    args = parser.parse_args()

    # If no directory provided, try using GUI dialog (fallback for backward compatibility)
    if not args.directory:
        try:
            import tkinter.filedialog as fd
            print("No directory argument provided. Opening selection dialog...")
            args.directory = fd.askdirectory()
        except ImportError:
            print("Error: No directory provided and tkinter is not available. Please provide a directory argument.")
            sys.exit(1)
        except Exception as e:
            # Handle headless environments
            print(f"Error opening dialog: {e}")
            print("Please provide a directory argument: python file_organizer.py <directory>")
            sys.exit(1)

    if not args.directory:
        print("No directory selected.")
        sys.exit(1)

    root = Path(args.directory)
    if not root.exists():
        print(f"Error: Directory '{root}' does not exist.")
        sys.exit(1)

    print(f"Processing directory: {root}")
    resolve_duplicates(root, dry_run=args.dry_run)

    csv_path = Path(args.csv) if args.csv else root / 'file_report.csv'
    generate_csv(root, csv_path)

if __name__ == '__main__':
    main()
