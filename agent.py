# Research Agent - Step 4: Multiple Search Sources
# ==================================================
# Now our agent searches across multiple sources:
# Wikipedia, DuckDuckGo, Reddit, and NewsAPI.

import json
import os  # For reading environment variables (like API keys)
import urllib.request
import urllib.parse


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


# =============================================================
#  API HELPERS
# =============================================================


def fetch_url(url):
    """Fetch data from a URL and return it as a Python dictionary."""
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ResearchAgent/1.0 (educational project)"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            data = response.read()
            text = data.decode("utf-8")
            return json.loads(text)
    except Exception as error:
        print(f"  [Error fetching data: {error}]")
        return None


# =============================================================
#  SOURCE 1: WIKIPEDIA
# =============================================================


def search_wikipedia(query):
    """Search Wikipedia for background knowledge on a topic."""
    print("\n  Searching Wikipedia...")

    encoded_query = urllib.parse.quote(query)
    search_url = (
        f"https://en.wikipedia.org/w/api.php"
        f"?action=opensearch&search={encoded_query}&limit=3&format=json"
    )

    search_data = fetch_url(search_url)
    if search_data is None or len(search_data) < 4:
        return []

    titles = search_data[1]
    urls = search_data[3]

    results = []
    for title, url in zip(titles, urls):
        encoded_title = urllib.parse.quote(title)
        summary_url = (
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
        )

        summary_data = fetch_url(summary_url)
        if summary_data and "extract" in summary_data:
            summary = summary_data["extract"]
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


# =============================================================
#  SOURCE 2: DUCKDUCKGO
# =============================================================
# DuckDuckGo has an "Instant Answer" API — free, no key needed.
# It returns quick facts and related topics for a search query.


def search_duckduckgo(query):
    """Search DuckDuckGo for web results and instant answers.

    Parameters:
        query (str): What to search for.

    Returns:
        list: A list of result dictionaries.
    """
    print("  Searching DuckDuckGo...")

    encoded_query = urllib.parse.quote(query)
    url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"

    data = fetch_url(url)
    if data is None:
        return []

    results = []

    # DuckDuckGo returns an "Abstract" — a short summary from a source
    if data.get("Abstract"):
        results.append({
            "title": data.get("Heading", "DuckDuckGo Result"),
            "summary": data["Abstract"][:300] + "..." if len(data["Abstract"]) > 300 else data["Abstract"],
            "url": data.get("AbstractURL", ""),
            "source": "DuckDuckGo",
        })

    # It also returns "RelatedTopics" — links to related subjects
    # --- CONCEPT: Nested Data ---
    # API responses often have data inside data (dicts inside lists inside dicts).
    # You need to navigate through the layers to find what you want.
    for topic in data.get("RelatedTopics", [])[:3]:
        # Some topics are grouped, some are direct — we only want direct ones
        if "Text" in topic:
            results.append({
                "title": topic.get("Text", "")[:80],
                "summary": topic.get("Text", ""),
                "url": topic.get("FirstURL", ""),
                "source": "DuckDuckGo",
            })

    print(f"  Found {len(results)} DuckDuckGo result(s).")
    return results


# =============================================================
#  SOURCE 3: REDDIT
# =============================================================
# Reddit has a public JSON API. You can get JSON from almost any
# Reddit page by adding ".json" to the URL. No key needed!


def search_reddit(query):
    """Search Reddit for community discussions on a topic.

    Reddit is great for real opinions, reviews, and discussions
    that you won't find in encyclopedias or news articles.

    Note: Reddit blocks many automated requests. We use a more
    descriptive User-Agent to be polite, but if it still fails,
    we skip gracefully.

    Parameters:
        query (str): What to search for.

    Returns:
        list: A list of result dictionaries.
    """
    print("  Searching Reddit...")

    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://www.reddit.com/search.json"
        f"?q={encoded_query}&sort=relevance&limit=3&t=year"
    )

    # --- CONCEPT: Custom Headers ---
    # Some APIs require specific headers to allow access.
    # Reddit wants a descriptive User-Agent string.
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "python:ResearchAgent:v1.0 (educational project)",
            },
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        print(f"  [Reddit unavailable: {error}]")
        return []

    results = []

    # --- CONCEPT: Navigating Complex JSON ---
    # Reddit's API nests data deeply:
    #   data -> data -> children -> [each post] -> data -> title
    # You chain dictionary lookups to dig through the layers.
    posts = data.get("data", {}).get("children", [])

    for post in posts:
        post_data = post.get("data", {})
        title = post_data.get("title", "No title")
        selftext = post_data.get("selftext", "")
        subreddit = post_data.get("subreddit", "unknown")
        permalink = post_data.get("permalink", "")
        score = post_data.get("score", 0)
        num_comments = post_data.get("num_comments", 0)

        # Build a useful summary from the post data
        summary = f"r/{subreddit} | {score} upvotes | {num_comments} comments"
        if selftext:
            # Show a preview of the post text
            preview = selftext[:200] + "..." if len(selftext) > 200 else selftext
            summary += f"\n      {preview}"

        results.append({
            "title": title,
            "summary": summary,
            "url": f"https://www.reddit.com{permalink}",
            "source": "Reddit",
        })

    print(f"  Found {len(results)} Reddit post(s).")
    return results


# =============================================================
#  SOURCE 4: NEWSAPI
# =============================================================
# NewsAPI requires a free API key from https://newsapi.org
# We read the key from an environment variable so it stays private.
#
# --- CONCEPT: Environment Variables ---
# Environment variables are settings stored OUTSIDE your code.
# This keeps secrets (like API keys) out of your code files,
# so you don't accidentally share them on GitHub.


def search_news(query):
    """Search recent news articles using NewsAPI.

    Requires a NEWSAPI_KEY environment variable to be set.
    If not set, this source is skipped gracefully.

    Parameters:
        query (str): What to search for.

    Returns:
        list: A list of result dictionaries.
    """
    # --- CONCEPT: os.environ ---
    # os.environ.get() reads an environment variable.
    # The second argument is a default if the variable isn't set.
    api_key = os.environ.get("NEWSAPI_KEY", "")

    if not api_key:
        print("  Skipping NewsAPI (no API key set).")
        print("  To enable: export NEWSAPI_KEY='your-key-here'")
        print("  Get a free key at: https://newsapi.org")
        return []

    print("  Searching NewsAPI...")

    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={encoded_query}&sortBy=relevancy&pageSize=3"
        f"&apiKey={api_key}"
    )

    data = fetch_url(url)
    if data is None or data.get("status") != "ok":
        return []

    results = []

    for article in data.get("articles", [])[:3]:
        title = article.get("title", "No title")
        description = article.get("description", "No description available.")
        source_name = article.get("source", {}).get("name", "Unknown")
        article_url = article.get("url", "")
        published = article.get("publishedAt", "")[:10]  # Just the date

        summary = f"[{source_name}] ({published}) {description}"
        if len(summary) > 300:
            summary = summary[:300] + "..."

        results.append({
            "title": title,
            "summary": summary,
            "url": article_url,
            "source": "NewsAPI",
        })

    print(f"  Found {len(results)} news article(s).")
    return results


# =============================================================
#  DISPLAY RESULTS
# =============================================================


def display_results(results, category):
    """Display research results to the user."""
    if not results:
        print("\n  No results found. Try rephrasing your question.")
        return

    print(f"\n{'═' * 50}")
    print(f"  RESEARCH RESULTS — {category}")
    print(f"{'═' * 50}")

    # --- CONCEPT: Grouping Results ---
    # We group results by source so the output is organized.
    # This uses a pattern: loop through, check source, print headers.
    current_source = None
    result_num = 1

    for result in results:
        if result["source"] != current_source:
            current_source = result["source"]
            print(f"\n  ── {current_source} ──")

        print(f"\n  [{result_num}] {result['title']}")
        print(f"      {result['summary']}")
        print(f"      Link: {result['url']}")
        result_num += 1

    print(f"\n{'═' * 50}")
    print(f"  Total: {len(results)} result(s) from {_count_sources(results)} source(s)")
    print(f"{'═' * 50}")


def _count_sources(results):
    """Count unique sources in the results."""
    sources = set()
    for result in results:
        sources.add(result["source"])
    return len(sources)


# =============================================================
#  MAIN
# =============================================================


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

    # --- Gather results from ALL sources ---
    all_results = []

    # Source 1: Wikipedia (background knowledge)
    all_results.extend(search_wikipedia(question))

    # Source 2: DuckDuckGo (web search)
    all_results.extend(search_duckduckgo(question))

    # Source 3: Reddit (community discussions)
    all_results.extend(search_reddit(question))

    # Source 4: NewsAPI (recent news — needs API key)
    all_results.extend(search_news(question))

    # --- Display everything ---
    display_results(all_results, category)


if __name__ == "__main__":
    main()
