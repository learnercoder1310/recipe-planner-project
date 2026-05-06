"""
Web scraper using BeautifulSoup.
Extracts meaningful text from recipe pages while removing noise (nav, ads, scripts).
"""

import requests
from bs4 import BeautifulSoup


# Headers to mimic a real browser (avoids 403 blocks)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Tags that almost never contain recipe content
NOISE_TAGS = [
    "script", "style", "nav", "footer", "header",
    "aside", "advertisement", "iframe", "noscript",
    "form", "button", "svg", "meta", "link",
]


def scrape_recipe_page(url: str, timeout: int = 15) -> str:
    """
    Fetch a recipe page and return its cleaned plain-text content.

    Args:
        url: The recipe blog URL.
        timeout: HTTP request timeout in seconds.

    Returns:
        A cleaned string of the page's textual content.

    Raises:
        ValueError: If the URL is unreachable or returns a non-200 status.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Cannot connect to URL: {url}")
    except requests.exceptions.Timeout:
        raise ValueError(f"Request timed out for URL: {url}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"HTTP error: {e}")

    if response.status_code != 200:
        raise ValueError(
            f"URL returned status {response.status_code}. "
            "Make sure the URL is publicly accessible."
        )

    soup = BeautifulSoup(response.content, "html.parser")

    # Remove noisy tags
    for tag in soup(NOISE_TAGS):
        tag.decompose()

    # Try to focus on the main content area first (common recipe site selectors)
    content_candidates = [
        soup.find("article"),
        soup.find("main"),
        soup.find(class_=lambda c: c and "recipe" in c.lower()),
        soup.find(id=lambda i: i and "recipe" in i.lower()),
        soup.find(class_=lambda c: c and "content" in c.lower()),
        soup.body,
    ]

    main_content = next((c for c in content_candidates if c), soup)

    # Extract text
    raw_text = main_content.get_text(separator="\n", strip=True)

    # Clean: remove blank lines and very short lines (< 3 chars, usually noise)
    lines = [line.strip() for line in raw_text.splitlines()]
    cleaned_lines = [line for line in lines if len(line) > 2]
    cleaned_text = "\n".join(cleaned_lines)

    # Limit to ~8000 chars so we stay within LLM context safely
    return cleaned_text[:8000]
