# Research Agent - Step 3: Working with APIs
# =============================================
# APIs (Application Programming Interfaces) let your code talk to
# services on the internet. You send a request, and get data back.

# --- CONCEPT: Imports ---
# 'import' brings in code that others have written so you can use it.
# These are part of Python's "standard library" — they come pre-installed.
import json  # For working with JSON data (the format APIs use)
import urllib.request  # For making web requests
import urllib.parse  # For formatting URLs safely


def greet_user():
    """Display a welcome message to the user."""
    print("=" * 50)
    print("  RESEARCH AGENT — Business & Startup Research")
    print("=" * 50)
    print()
    print("I help you research markets, competitors,")
    print("trends, and business ideas.")
    print()


def get_question():
    """Ask the user for a research question and return it."""
    question = input("What would you like to research? ")
    question = question.strip()

    if question == "":
        return None
    return question


def categorize_question(question):
    """Figure out what type of research the user wants."""
    question_lower = question.lower()

    categories = {
        "competitor": "Competitor Analysis",
        "market": "Market Research",
        "trend": "Trend Analysis",
        "startup": "Startup Research",
        "price": "Pricing Research",
        "customer": "Customer Research",
        "invest": "Investment Research",
        "fund": "Funding Research",
    }

    for keyword, category in categories.items():
        if keyword in question_lower:
            return category

    return "General Business Research"


# --- CONCEPT: Making API Calls ---
# An API call is like visiting a website, but instead of getting a
# webpage, you get structured data (usually in JSON format).
# JSON looks like Python dictionaries — {"key": "value"}


def fetch_url(url):
    """Fetch data from a URL and return it as a Python dictionary.

    This is a helper function — it handles the repetitive work of
    making web requests so other functions don't have to.

    Parameters:
        url (str): The URL to fetch data from.

    Returns:
        dict: The JSON response parsed into a Python dictionary,
              or None if the request failed.
    """
    # --- CONCEPT: Try/Except (Error Handling) ---
    # Sometimes things go wrong (no internet, bad URL, etc.).
    # try/except lets your program handle errors gracefully
    # instead of crashing.
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ResearchAgent/1.0"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            data = response.read()
            # .decode() converts raw bytes into a string
            text = data.decode("utf-8")
            # json.loads() converts a JSON string into a Python dictionary
            return json.loads(text)
    except Exception as error:
        print(f"  [Error fetching data: {error}]")
        return None


def search_wikipedia(query):
    """Search Wikipedia for articles related to the query.

    Wikipedia has a free API — no account or key needed!
    We use two endpoints:
      1. Search — find relevant article titles
      2. Summary — get a summary of each article

    Parameters:
        query (str): What to search for.

    Returns:
        list: A list of dictionaries, each with 'title', 'summary', and 'url'.
    """
    print("\n  Searching Wikipedia...")

    # --- CONCEPT: URL Encoding ---
    # URLs can't have spaces or special characters.
    # urllib.parse.quote() converts "meal kit delivery" to "meal%20kit%20delivery"
    encoded_query = urllib.parse.quote(query)

    # Step 1: Search for matching article titles
    search_url = (
        f"https://en.wikipedia.org/w/api.php"
        f"?action=opensearch&search={encoded_query}&limit=3&format=json"
    )

    search_data = fetch_url(search_url)
    if search_data is None or len(search_data) < 4:
        return []

    # Wikipedia's opensearch returns: [query, [titles], [descriptions], [urls]]
    titles = search_data[1]
    urls = search_data[3]

    # Step 2: Get a summary for each article
    results = []
    for title, url in zip(titles, urls):
        encoded_title = urllib.parse.quote(title)
        summary_url = (
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
        )

        summary_data = fetch_url(summary_url)
        if summary_data and "extract" in summary_data:
            summary = summary_data["extract"]
            # Truncate long summaries to keep output readable
            if len(summary) > 300:
                summary = summary[:300] + "..."

            results.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": "Wikipedia",
            })

    print(f"  Found {len(results)} Wikipedia article(s).")
    return results


def display_results(results, category):
    """Display research results to the user.

    Parameters:
        results (list): List of result dictionaries.
        category (str): The research category.
    """
    if not results:
        print("\n  No results found. Try rephrasing your question.")
        return

    print(f"\n{'═' * 50}")
    print(f"  RESEARCH RESULTS — {category}")
    print(f"{'═' * 50}")

    for i, result in enumerate(results, start=1):
        print(f"\n  [{i}] {result['title']}")
        print(f"      Source: {result['source']}")
        print(f"      {result['summary']}")
        print(f"      Link: {result['url']}")

    print(f"\n{'═' * 50}")
    print(f"  Total: {len(results)} result(s) from {_count_sources(results)} source(s)")
    print(f"{'═' * 50}")


def _count_sources(results):
    """Count the number of unique sources in the results.

    The underscore prefix is a Python convention meaning
    'this is a helper function, not meant to be called directly.'
    """
    # --- CONCEPT: Sets ---
    # A set is like a list, but it only keeps unique values.
    # Great for counting distinct items.
    sources = set()
    for result in results:
        sources.add(result["source"])
    return len(sources)


def main():
    """Run the research agent."""
    greet_user()

    question = get_question()

    if question is None:
        print("No question entered. Goodbye!")
        return

    category = categorize_question(question)
    print(f"\n  Category: {category}")
    print(f"  Researching: {question}")

    # --- Gather results from all sources ---
    all_results = []

    # Source 1: Wikipedia
    wiki_results = search_wikipedia(question)
    all_results.extend(wiki_results)

    # (More sources coming in Step 4!)

    # --- Display everything ---
    display_results(all_results, category)


if __name__ == "__main__":
    main()
