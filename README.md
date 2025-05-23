# Website Crawler to Markdown

This script crawls a website starting from a given URL, extracts the content of pages within a specified base URL, converts the HTML content to Markdown, and saves the individual Markdown files. Finally, it concatenates all the saved Markdown files into a single output file.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone git@github.com:khajaphysist/docs4llm.git
    cd docs4llm
    ```

2.  **Install dependencies:**

    This script requires Python 3.7+ and several libraries. It uses Playwright as the page visiter, which requires browser binaries.

    Make sure you have `uv` installed. If not, follow the instructions [here](https://github.com/astral-sh/uv).

    ```bash
    uv sync
    playwright install
    ```

## Usage

The script is run from the command line.

```bash
uv run main.py <start_url> <base_url> <output_file_path> [--max-pages <max_pages>]
```

### Parameters

*   `<start_url>`: The URL where the crawling will begin.
*   `<base_url>`: The base URL used to filter the links found on the pages. Only links that start with this base URL will be followed.
*   `<output_file_path>`: The path where the final concatenated Markdown file will be saved. The directory for this file will be created if it doesn't exist.
*   `--max-pages <max_pages>` (optional): An integer specifying the maximum number of pages to visit during the crawl. If not provided, the script will attempt to crawl all pages found within the `base_url`.

### Created Directories

The script will create a directory named `data` in the same location as the `main.py` script to store the individual Markdown files before concatenating them.

## Example

```bash
uv run main.py https://docs.trychroma.com/docs/overview/introduction https://docs.trychroma.com/docs ./output/chroma_docs.md --max-pages 50
```

This command will:

1.  Start crawling from `https://docs.trychroma.com/docs/overview/introduction`.

2.  Only follow links that start with `https://docs.trychroma.com/docs`.

3.  Save individual markdown files in the `./data/` directory.

4.  Stop after visiting a maximum of 50 pages.

5.  Concatenate all the saved markdown files from `./data/` into
    `./output/chroma_docs.md`.
