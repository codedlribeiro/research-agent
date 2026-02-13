# Research Agent - Step 5: AI-Powered Reasoning
# ================================================
# Now our agent uses Claude to THINK about the results —
# summarizing, comparing viewpoints, and creating action plans.

import json
import os
import urllib.request
import urllib.parse

# --- CONCEPT: Third-Party Libraries ---
# Unlike 'json' and 'os' which come with Python, 'anthropic' is a
# third-party library we installed with 'pip3 install anthropic'.
# We use try/except on the import so the program doesn't crash
# if it's not installed yet.
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


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


def search_duckduckgo(query):
    """Search DuckDuckGo for web results and instant answers."""
    print("  Searching DuckDuckGo...")

    encoded_query = urllib.parse.quote(query)
    url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"

    data = fetch_url(url)
    if data is None:
        return []

    results = []

    if data.get("Abstract"):
        results.append({
            "title": data.get("Heading", "DuckDuckGo Result"),
            "summary": data["Abstract"][:300] + "..." if len(data["Abstract"]) > 300 else data["Abstract"],
            "url": data.get("AbstractURL", ""),
            "source": "DuckDuckGo",
        })

    for topic in data.get("RelatedTopics", [])[:3]:
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


def search_reddit(query):
    """Search Reddit for community discussions on a topic."""
    print("  Searching Reddit...")

    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://www.reddit.com/search.json"
        f"?q={encoded_query}&sort=relevance&limit=3&t=year"
    )

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
    posts = data.get("data", {}).get("children", [])

    for post in posts:
        post_data = post.get("data", {})
        title = post_data.get("title", "No title")
        selftext = post_data.get("selftext", "")
        subreddit = post_data.get("subreddit", "unknown")
        permalink = post_data.get("permalink", "")
        score = post_data.get("score", 0)
        num_comments = post_data.get("num_comments", 0)

        summary = f"r/{subreddit} | {score} upvotes | {num_comments} comments"
        if selftext:
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


def search_news(query):
    """Search recent news articles using NewsAPI."""
    api_key = os.environ.get("NEWSAPI_KEY", "")

    if not api_key:
        print("  Skipping NewsAPI (no API key set).")
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
        published = article.get("publishedAt", "")[:10]

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
#  AI-POWERED ANALYSIS (NEW IN STEP 5!)
# =============================================================
# This is where the magic happens. Instead of just showing raw
# results, we send them to Claude (an AI) to:
#   1. Summarize the key findings
#   2. Compare different viewpoints
#   3. Create an action plan
#
# --- CONCEPT: LLM (Large Language Model) ---
# An LLM is an AI that understands and generates text.
# You talk to it by sending a "prompt" (your instructions)
# and it sends back a response. It's like texting a very
# smart assistant.


def analyze_with_ai(question, results, category):
    """Use Claude to analyze research results and provide insights.

    This function sends all the raw results to Claude along with
    instructions on how to analyze them. Claude returns a
    structured analysis with summaries, viewpoints, and action plans.

    Parameters:
        question (str): The original research question.
        results (list): All search results gathered.
        category (str): The research category.

    Returns:
        str: Claude's analysis, or None if AI is unavailable.
    """
    # Check if we can use AI
    if not HAS_ANTHROPIC:
        print("\n  [AI analysis unavailable — run: pip3 install anthropic]")
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("\n  [AI analysis unavailable — no ANTHROPIC_API_KEY set]")
        print("  To enable: export ANTHROPIC_API_KEY='your-key-here'")
        return None

    print("\n  Analyzing results with AI...")

    # --- CONCEPT: Preparing Data for the AI ---
    # We need to convert our results into text that Claude can read.
    # This is called "building a prompt" — the better your prompt,
    # the better the AI's response.
    results_text = ""
    for i, result in enumerate(results, start=1):
        results_text += f"\n--- Result {i} ---\n"
        results_text += f"Title: {result['title']}\n"
        results_text += f"Source: {result['source']}\n"
        results_text += f"Summary: {result['summary']}\n"
        results_text += f"URL: {result['url']}\n"

    # --- CONCEPT: System Prompt vs User Prompt ---
    # When talking to an LLM, you typically send two things:
    #   - System prompt: Sets the AI's role and behavior
    #   - User prompt: The actual question or task
    system_prompt = """You are a business research analyst. Your job is to analyze
research results and provide clear, actionable insights.

Always structure your response with these sections:
1. SUMMARY — A brief overview of what the research found (2-3 sentences)
2. KEY FINDINGS — Bullet points of the most important facts
3. DIFFERENT VIEWPOINTS — If the sources show different perspectives, highlight them
4. ACTION PLAN — 3-5 concrete next steps the user could take based on the research

Keep your response concise and focused on business value.
If the results are limited or not very relevant, say so honestly
and suggest better search terms."""

    user_prompt = f"""Research Question: {question}
Category: {category}

Here are the research results I gathered from multiple sources:
{results_text}

Please analyze these results and provide your structured analysis."""

    # --- CONCEPT: Making an API Call to an LLM ---
    # We create a "client" (our connection to Claude), then send
    # a message with our prompts. The API returns Claude's response.
    try:
        client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY automatically

        # --- CONCEPT: API Parameters ---
        # model: Which AI model to use (haiku is fast and cheap)
        # max_tokens: Maximum length of the response
        # messages: The conversation (role + content pairs)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )

        # The response contains a list of content blocks
        # We extract the text from the first one
        response_text = message.content[0].text
        return response_text

    except Exception as error:
        print(f"  [AI analysis error: {error}]")
        return None


# =============================================================
#  DISPLAY RESULTS
# =============================================================


def display_results(results, category):
    """Display raw research results to the user."""
    if not results:
        print("\n  No results found. Try rephrasing your question.")
        return

    print(f"\n{'═' * 50}")
    print(f"  RAW RESULTS — {category}")
    print(f"{'═' * 50}")

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


def display_analysis(analysis):
    """Display the AI's analysis to the user.

    Parameters:
        analysis (str): The AI-generated analysis text.
    """
    print(f"\n{'═' * 50}")
    print(f"  AI ANALYSIS")
    print(f"{'═' * 50}")
    print()
    print(analysis)
    print(f"\n{'═' * 50}")


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

    # --- Phase 1: Gather results from ALL sources ---
    all_results = []
    all_results.extend(search_wikipedia(question))
    all_results.extend(search_duckduckgo(question))
    all_results.extend(search_reddit(question))
    all_results.extend(search_news(question))

    # --- Phase 2: Show raw results ---
    display_results(all_results, category)

    # --- Phase 3: AI Analysis (NEW!) ---
    if all_results:
        analysis = analyze_with_ai(question, all_results, category)
        if analysis:
            display_analysis(analysis)


if __name__ == "__main__":
    main()
