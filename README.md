# EPUB Content Scanner

A Python script designed to scan `.epub` files for a user-defined list of words and phrases. It's built to help verify the content of ebooks, particularly for ensuring children's books have not been tampered with. The script identifies files containing specific terms, reports the context in which they were found, and prompts the user for action, such as deletion of the file.

## Features

* Scans a target folder and all its subdirectories for `.epub` files.
* Uses customizable word lists for scanning.
* Aggregates search terms from multiple word list files.
* Handles various text encodings in word list files automatically.
* Provides context for each match by showing the full sentence.
* Prompts the user to delete flagged files and can clean up empty parent directories.
* Robust error handling for corrupted EPUB files or unreadable sections.

---

## Prerequisites

This script relies on external Python libraries. You must have them installed to run it.

* **Python 3.x**
* **Required Libraries**: `EbookLib` and `BeautifulSoup4`

You can install the necessary libraries using pip:
```bash
pip install EbookLib beautifulsoup4
```

---

## How to Use

1.  **Place the Script**: Put the `EPUB File Scanner.py` script in a folder.
2.  **Prepare Word Lists**: Place your inappropriate word list text files in the folder you intend to scan. Template lists for English, German, and French are provided in this repository.
3.  **Run the Script**: Open a terminal or command prompt and execute the script.

There are two ways to run the script:

**Option A: Scan the Current Folder**
Navigate to the folder containing your `.epub` files and run the script without any arguments. It will scan its own directory.
```bash
python "EPUB File Scanner.py"
```

**Option B: Scan a Specific Folder**
Run the script with the path to your target folder as a command-line argument.
```bash
python "EPUB File Scanner.py" "C:\Path\To\Your\Ebook\Collection"
```

---

## Configuration: The Word Lists

The script's scanning behavior is controlled by simple text files.

* **File Naming**: The script will automatically find and load any `.txt` file in the target scan directory whose name contains the word `inappropriate` (case-insensitive).
    * *Examples*: `Inappropriate Word List English.txt`, `my-inappropriate-words.txt`

* **File Format**:
    * Each word or phrase must be on a new line.
    * Leading/trailing spaces are automatically removed.
    * Lines starting with a hash (`#`) are treated as comments and ignored.
    * Empty lines are ignored.
    * You can use multiple files (e.g., one for each language), and the script will combine them into a single, unique list of search terms.

* **Templates**: This repository includes starter word lists for English, German, and French. Use them as a base, edit them, or create your own from scratch.

### A Note on False Positives and Best Practices

A "false positive" occurs when the script flags a word that is used in a perfectly normal context (e.g., flagging the word `cock` in the phrase "to cock a gun"). The key to making this script effective is managing your word lists to minimize these errors.

* **Refine Your Lists**: The provided template lists are starting points. You may find that some words are too ambiguous and generate too many false positives in the types of books you scan. Feel free to remove them to reduce noise.
* **Isolate Languages**: The script loads **all** `*inappropriate*.txt` files from the target directory. If you are scanning English books, ensure **only the English word list** is in that folder. Having French or German lists present can cause cross-language false positives (e.g., the French word `bite` matching the English word "bite").

---

## How It Works

The script operates in a straightforward sequence:

1.  **Dependency Check**: First, it verifies that the required libraries (`EbookLib`, `BeautifulSoup4`) are installed. If not, it provides instructions and exits.
2.  **Target Directory Identification**: It determines which folder to scan based on the command-line arguments.
3.  **Word List Loading**: It searches the target directory for any `*inappropriate*.txt` files, reads them, and compiles a unique set of search terms. If no files are found, it falls back to a small, predefined list.
4.  **Regex Compilation**: For performance, it compiles the final word list into a single, case-insensitive regular expression that matches only whole words.
5.  **EPUB Discovery**: It walks through the target directory and all subdirectories to find every file ending with `.epub`.
6.  **Scanning**: For each EPUB file:
    * It opens the file and iterates through its internal contents.
    * It processes only the HTML/XHTML text documents, ignoring images and other assets to prevent errors.
    * The text is extracted, split into sentences, and each sentence is checked against the compiled regex pattern.
7.  **Reporting & Action**:
    * If matches are found, the script lists the problematic sentences.
    * It then prompts the user to either list all instances (if there are many), delete the file, or skip it.
    * If a file is deleted and its containing folder becomes empty, the folder is also removed.
    * If a file is clean, it is reported as such. If a file is corrupt or unreadable, an error is logged, and the script moves on to the next file.


## License

The **EPUB Content Scanner** script itself is released under the [MIT License](https://opensource.org/licenses/MIT).

This project depends on third-party libraries that are distributed under their own licenses:

* **EbookLib**: [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html) [EbookLib Github Link](https://github.com/aerkalov/ebooklib)
* **BeautifulSoup4**: [MIT License](https://opensource.org/licenses/MIT) [Python Package Index Link](https://pypi.org/project/beautifulsoup4/)
