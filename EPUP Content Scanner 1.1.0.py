# --- Dependency Check ---
# Verify that all required libraries are installed before proceeding.
try:
    import sys
    import os, time
    import re
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError as e:
    missing_module = str(e).split("'")[1]
    print(f"Error: Missing required library '{missing_module}'.")
    print("Please install the necessary libraries by running:")
    print("pip install EbookLib beautifulsoup4")
    print("Exiting...")
    time.sleep(3)
    sys.exit(1)


def load_words_to_check(search_paths):
    """
    Loads search terms from all .txt files in the specified search paths
    that contain "inappropriate" in their filename (case-insensitive).
    It attempts to read files with multiple common encodings.

    Args:
        search_paths (set): A set of unique directories to search for word list files.

    Returns:
        list: A list of unique words/phrases to search for.
    """
    fallback_words = [
        "sperm",
        "penis",
        "sex",
        "orgasm",
        "orgasmus"
    ]
    words = set()
    files_loaded = set() # Use a set to show a unique list of filenames loaded.
    encodings_to_try = ['utf-8', 'utf-16', 'utf-16-le', 'latin-1']

    for path in search_paths:
        try:
            for filename in os.listdir(path):
                if "inappropriate" in filename.lower() and filename.lower().endswith('.txt'):
                    config_path = os.path.join(path, filename)
                    content_read = False
                    for encoding in encodings_to_try:
                        try:
                            with open(config_path, 'r', encoding=encoding) as f:
                                lines_from_file = [
                                    line.strip() for line in f
                                    if line.strip() and not line.strip().startswith('#')
                                ]
                                if lines_from_file:
                                    words.update(lines_from_file)
                                    files_loaded.add(f"{filename} (as {encoding})")
                                content_read = True
                                break 
                        except UnicodeDecodeError:
                            continue
                        except Exception as e:
                            print(f"\nWarning: Could not read '{filename}'. Error: {e}.")
                            break
                    
                    if not content_read:
                         print(f"\nWarning: Could not decode '{filename}' with any of the attempted encodings.")
        except FileNotFoundError:
            # This path might not exist (e.g., a typo in user input), so just skip it.
            continue
        except Exception as e:
            print(f"\nAn error occurred while searching directory '{path}': {e}.")

    if words:
        print(f"\nLoaded {len(words)} unique words/phrases from: {', '.join(sorted(list(files_loaded)))}.")
        return list(words)
    else:
        print(f"\nNo readable '*inappropriate*.txt' files found in specified paths:")
        for i in search_paths:
            print(i)
        print(f"\nUsing the fallback list (very crude): {fallback_words}")
        return fallback_words

def check_for_inappropriate_words(file_path, search_pattern):
    """
    Scans an .epub file using a pre-compiled regex pattern.

    Args:
        file_path (str): The full path to the .epub file.
        search_pattern (re.Pattern): The compiled regex pattern to search for.

    Returns:
        list: A list of unique sentences containing matched words.
        None: If the file is scanned successfully and is clean.
        False: If an error occurred that prevented a full scan.
    """
    print(f"--> Checking '{os.path.basename(file_path)}'...")
    
    found_sentences = set()

    try:
        # ignore_ncx option suppresses a common UserWarning for older EPUBs.
        book = epub.read_epub(file_path, options={"ignore_ncx": True})
        all_text = []

        # Iterate through all items and process only the HTML/XHTML content.
        for item in book.get_items():
            try:
                # This check ensures we only process text documents, skipping images, etc.
                if isinstance(item, epub.EpubHtml):
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    all_text.append(soup.get_text(separator=' ', strip=True))
            except Exception as e:
                # Log an error for a specific section but continue with the rest of the book.
                item_name = item.get_name() or 'Unnamed Item'
                print(f"    [Warning] Could not process section '{item_name}'. Reason: {e}")
                continue
        
        if not all_text:
            print(f"    [Error] Skipping \"{os.path.basename(file_path)}\" because no readable text content was found.")
            return False

        full_text = ' '.join(all_text)
        # Split text into sentences based on common terminators.
        sentences = re.split(r'(?<=[.?!])\s+', full_text)

        for sentence in sentences:
            if search_pattern.search(sentence):
                found_sentences.add(sentence.strip())

    except Exception as e:
        # Catches file-level errors (e.g., corrupt zip structure).
        print(f"    [Error] Could not process EPUB \"{os.path.basename(file_path)}\". Reason: The file may be corrupt. ({e})")
        return False

    if found_sentences:
        return list(found_sentences)
    else:
        # Return None for a clean scan to differentiate from an error (False).
        return None

def prompt_user_to_delete(file_path, sentences):
    """
    Presents flagged content to the user and asks for confirmation to delete.

    Args:
        file_path (str): The full path to the file in question.
        sentences (list): The list of sentences that triggered the flag.
    """
    instance_count = len(sentences)
    print(f"\n[!] Inappropriate content found in: {file_path}")
    print(f"    Found {instance_count} unique sentence(s) with inappropriate words/phrases.")

    should_delete = False
    
    if instance_count > 10:
        while True:
            response = input("    List all instances (l), delete file directly (d), or skip (s)? (l/d/s): ").lower()
            if response == 'l':
                for sentence in sentences:
                    print(f'    - "{sentence}"')
                
                delete_response = input("\n    Do you want to delete this file? (y/n): ").lower()
                if delete_response == 'y':
                    should_delete = True
                break
            elif response == 'd':
                should_delete = True
                break
            elif response == 's':
                break
            else:
                print("    Invalid input. Please enter 'l', 'd', or 's'.")
    else:
        print("    The following sentences were flagged:")
        for sentence in sentences:
            print(f'    - "{sentence}"')
        
        while True:
            response = input("\n    Do you want to delete this file? (y/n): ").lower()
            if response == 'y':
                should_delete = True
                break
            elif response == 'n':
                break
            else:
                print("    Invalid input. Please enter 'y' or 'n'.")

    if should_delete:
        try:
            parent_directory = os.path.dirname(file_path)
            print(f"    Deleting file: {file_path}...")
            os.remove(file_path)
            print("    File deleted.")

            # If the parent directory is now empty, remove it.
            if not os.listdir(parent_directory):
                print(f"    Parent directory '{parent_directory}' is now empty. Deleting it...")
                os.rmdir(parent_directory)
                print("    Directory deleted.")

        except OSError as e:
            print(f"    Error during deletion: {e}")
    else:
        print(f"    Skipping \"{os.path.basename(file_path)}\" as requested by user.")
    print("")


def main():
    """
    Main function to drive the script.
    """
    epub_files = []
    scan_path = ""

    # Determine the target from command-line arguments.
    if len(sys.argv) == 2:
        path_from_arg = sys.argv[1]
        
        # Scenario 1: The path is a directory.
        if os.path.isdir(path_from_arg):
            scan_path = os.path.abspath(path_from_arg)
            print(f"Scanning the provided folder: {scan_path}")
            # Discover all .epub files within the directory.
            for root, dirs, files in os.walk(scan_path, topdown=True):
                for file in files:
                    if file.endswith(".epub"):
                        epub_files.append(os.path.join(root, file))

        # Scenario 2: The path is a single .epub file.
        elif os.path.isfile(path_from_arg) and path_from_arg.lower().endswith('.epub'):
            epub_files = [os.path.abspath(path_from_arg)]
            scan_path = os.path.dirname(epub_files[0]) # Use the file's directory for word lists.
            print(f"Scanning single file: {epub_files[0]}")
        
        # Scenario 3: The path is invalid.
        else:
            print(f"Error: The provided path '{path_from_arg}' is not a valid directory or .epub file.")
            sys.exit(1)

    # Scenario 4: No path provided, use the current working directory.
    elif len(sys.argv) == 1:
        scan_path = os.getcwd()
        print(f"Scan Path: {scan_path}")
        time.sleep(2)
        if scan_path.lower() == r'C:\Windows\System32'.lower():
            print(f"Current path {scan_path} is invalid.")
            scan_path = input("Please specify the path to the folder containing the EPUPs in question: ").strip().replace("\"", "")
            if not os.path.exists(scan_path):
                print("Exiting...") if scan_path == "" else print(f"Couldn't find {scan_path}. Exiting...")
                time.sleep(2)
                sys.exit()
        else:
            print(f"No folder provided. Scanning the current directory: {scan_path}")
        for root, dirs, files in os.walk(scan_path, topdown=True):
            for file in files:
                if file.endswith(".epub"):
                    epub_files.append(os.path.join(root, file))
    
    # Scenario 5: Too many arguments.
    else:
        print("Usage: python your_script_name.py [optional_path_to_folder_or_file]")
        time.sleep(2)
        sys.exit(1)

    # Identify the directory where the script itself is located.
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a set of unique directories to search for word lists.
    paths_to_search_for_words = {script_dir, scan_path}
    
    # Load search terms from both the script's directory and the target folder.
    words_to_check = load_words_to_check(paths_to_search_for_words)
    
    if not words_to_check:
        print("\nWord list is empty. Cannot proceed with scanning.")
        sys.exit(1)

    # Pre-compile the regex for performance.
    try:
        search_pattern = re.compile(
            r'\b(' + '|'.join(map(re.escape, words_to_check)) + r')\b', 
            re.IGNORECASE
        )
    except re.error as e:
        print(f"\n[Fatal Error] Could not compile regex from word list. Reason: {e}")
        sys.exit(1)

    # Report on files found and begin scanning.
    file_count = len(epub_files)
    if file_count == 0:
        print("No .epub files were found to scan.")
        sys.exit(0)
    
    print(f"\nFound {file_count} .epub file(s) to scan. Starting...\n")

    # Iterate through each found EPUB and scan it.
    for epub_path in epub_files:
        if not os.path.exists(epub_path):
            continue
            
        scan_result = check_for_inappropriate_words(epub_path, search_pattern)
        
        if isinstance(scan_result, list):
            prompt_user_to_delete(epub_path, scan_result)
        elif scan_result is None:
            print(f"--> '{os.path.basename(epub_path)}' is clean.\n")
        else: # Result is False, indicating an error.
            print("") # A specific error message was already printed inside the check function.

    print("Script finished.")

if __name__ == "__main__":
    main()
