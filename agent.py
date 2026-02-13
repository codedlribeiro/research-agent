# Research Agent - Step 6: Agent Loops & Memory
# ================================================
# The agent now LOOPS — it keeps running, remembers past research,
# and can refine its searches automatically.

import json
import os
import urllib.request
import urllib.parse

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


# =============================================================
#  MEMORY
# =============================================================
# --- CONCEPT: Classes ---
# A class is a blueprint for creating "objects" — things that
# hold both data AND functions together. Think of it like a
# template. Our Memory class is a template for creating a
# research memory that stores past findings.


class ResearchMemory:
    """Stores past research results across multiple queries.

    This gives the agent "memory" — it can reference past findings
    when analyzing new results, building a richer picture over time.
    """

    def __init__(self):
        """Initialize an empty memory.

        __init__ is a special method that runs when you create
        a new object from this class. 'self' refers to the
        specific object being created.
        """
        self.history = []  # List of past research rounds
        self.all_results = []  # Every result ever found

    def add_round(self, question, category, results, analysis):
        """Store a completed research round in memory.

        Parameters:
            question (str): What was researched.
            category (str): The research category.
            results (list): Raw results found.
            analysis (str): AI analysis of the results.
        """
        self.history.append({
            "question": question,
            "category": category,
            "result_count": len(results),
            "analysis": analysis,
        })
        self.all_results.extend(results)

    def get_context(self):
        """Build a text summary of past research for the AI.

        This is sent to Claude so it knows what was already researched.

        Returns:
            str: A summary of past research, or empty string if none.
        """
        if not self.history:
            return ""

        context = "\n\nPREVIOUS RESEARCH IN THIS SESSION:\n"
        for i, round_data in enumerate(self.history, start=1):
            context += f"\n--- Round {i} ---\n"
            context += f"Question: {round_data['question']}\n"
            context += f"Category: {round_data['category']}\n"
            context += f"Results found: {round_data['result_count']}\n"
            if round_data['analysis']:
                # Only include a snippet to keep the prompt manageable
                snippet = round_data['analysis'][:500]
                context += f"Analysis summary: {snippet}...\n"

        return context

    def get_round_count(self):
        """Return how many research rounds have been completed."""
        return len(self.history)


# =============================================================
#  UI FUNCTIONS
# =============================================================


def greet_user():
    """Display a welcome message to the user."""
    print("=" * 50)
    print("  RESEARCH AGENT — Business & Startup Research")
    print("=" * 50)
    print()
    print("I help you research markets, competitors,")
    print("trends, and business ideas.")
    print()
    print("  Type a question to research.")
    print("  Type 'quit' to exit.")
    print("  Type 'history' to see past research.")
    print()


def get_question():
    """Ask the user for a research question and return it."""
    question = input(">> What would you like to research? ")
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
#  SEARCH SOURCES
# =============================================================


def search_wikipedia(query):
    """Search Wikipedia for background knowledge on a topic."""
    print("  Searching Wikipedia...")

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


def gather_results(query):
    """Search all sources and return combined results.

    Parameters:
        query (str): The search query.

    Returns:
        list: Combined results from all sources.
    """
    all_results = []
    all_results.extend(search_wikipedia(query))
    all_results.extend(search_duckduckgo(query))
    all_results.extend(search_reddit(query))
    all_results.extend(search_news(query))
    return all_results


# =============================================================
#  AI-POWERED ANALYSIS
# =============================================================


def generate_search_terms(question):
    """Use AI to generate better search terms from the user's question.

    If the user asks "live selling on whatnot tiktok and ebay",
    Claude will break it into simpler terms that APIs can find:
    ["live commerce", "whatnot app", "tiktok shop", "ebay live"]

    Parameters:
        question (str): The user's original question.

    Returns:
        list: A list of simpler search terms, or [question] if AI unavailable.
    """
    if not HAS_ANTHROPIC or not os.environ.get("ANTHROPIC_API_KEY"):
        return [question]

    try:
        client = anthropic.Anthropic()

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system="""You generate search terms for research queries.
Given a user's question, return 2-4 simpler search terms that would
work well with Wikipedia and web search APIs. Return ONLY a JSON array
of strings, nothing else. Example: ["term one", "term two"]""",
            messages=[
                {"role": "user", "content": question}
            ],
        )

        response = message.content[0].text.strip()
        terms = json.loads(response)

        # Make sure we got a list of strings
        if isinstance(terms, list) and all(isinstance(t, str) for t in terms):
            print(f"  AI suggested search terms: {terms}")
            return terms

    except Exception:
        pass

    return [question]


def analyze_with_ai(question, results, category, memory):
    """Use Claude to analyze research results with memory context.

    Parameters:
        question (str): The original research question.
        results (list): All search results gathered.
        category (str): The research category.
        memory (ResearchMemory): Past research memory.

    Returns:
        str: Claude's analysis, or None if AI is unavailable.
    """
    if not HAS_ANTHROPIC:
        print("\n  [AI analysis unavailable — run: pip3 install anthropic]")
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("\n  [AI analysis unavailable — no ANTHROPIC_API_KEY set]")
        print("  To enable: export ANTHROPIC_API_KEY='your-key-here'")
        return None

    print("\n  Analyzing results with AI...")

    results_text = ""
    for i, result in enumerate(results, start=1):
        results_text += f"\n--- Result {i} ---\n"
        results_text += f"Title: {result['title']}\n"
        results_text += f"Source: {result['source']}\n"
        results_text += f"Summary: {result['summary']}\n"
        results_text += f"URL: {result['url']}\n"

    # --- CONCEPT: Context from Memory ---
    # We include past research so the AI can build on previous findings.
    memory_context = memory.get_context()

    system_prompt = """You are a business research analyst. Your job is to analyze
research results and provide clear, actionable insights.

Always structure your response with these sections:
1. SUMMARY — A brief overview of what the research found (2-3 sentences)
2. KEY FINDINGS — Bullet points of the most important facts
3. DIFFERENT VIEWPOINTS — If the sources show different perspectives, highlight them
4. ACTION PLAN — 3-5 concrete next steps the user could take based on the research
5. SUGGESTED FOLLOW-UPS — 2-3 follow-up questions the user could ask next

Keep your response concise and focused on business value.

IMPORTANT: If the search results are empty, limited, or not relevant,
use your own knowledge to answer the question as best you can.
Clearly note which information comes from search results vs your
own knowledge. Still provide all 5 sections above.

If previous research context is provided, reference it and build on it
rather than repeating the same information."""

    if results_text:
        user_prompt = f"""Research Question: {question}
Category: {category}
{memory_context}

Here are the research results I gathered from multiple sources:
{results_text}

Please analyze these results and provide your structured analysis."""
    else:
        user_prompt = f"""Research Question: {question}
Category: {category}
{memory_context}

My search sources returned no results for this query.
Please use your own knowledge to answer this research question
as thoroughly as you can. Provide your structured analysis."""

    try:
        client = anthropic.Anthropic()

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )

        return message.content[0].text

    except Exception as error:
        print(f"  [AI analysis error: {error}]")
        return None


# =============================================================
#  DISPLAY
# =============================================================


def display_results(results, category):
    """Display raw research results to the user."""
    if not results:
        print("\n  No results found.")
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
    """Display the AI's analysis to the user."""
    print(f"\n{'═' * 50}")
    print(f"  AI ANALYSIS")
    print(f"{'═' * 50}")
    print()
    print(analysis)
    print(f"\n{'═' * 50}")


def display_history(memory):
    """Show a summary of all past research in this session.

    Parameters:
        memory (ResearchMemory): The research memory object.
    """
    if memory.get_round_count() == 0:
        print("\n  No research history yet. Ask a question to get started!")
        return

    print(f"\n{'═' * 50}")
    print(f"  RESEARCH HISTORY ({memory.get_round_count()} rounds)")
    print(f"{'═' * 50}")

    for i, round_data in enumerate(memory.history, start=1):
        print(f"\n  Round {i}: {round_data['question']}")
        print(f"    Category: {round_data['category']}")
        print(f"    Results: {round_data['result_count']}")

    print(f"\n  Total results gathered: {len(memory.all_results)}")
    print(f"{'═' * 50}")


def _count_sources(results):
    """Count unique sources in the results."""
    sources = set()
    for result in results:
        sources.add(result["source"])
    return len(sources)


# =============================================================
#  MAIN — THE AGENT LOOP
# =============================================================
# --- CONCEPT: The Agent Loop ---
# Previously our agent ran once and exited. Now it LOOPS:
#   1. Ask a question
#   2. Search for answers
#   3. Analyze with AI
#   4. Store in memory
#   5. Go back to step 1
#
# This is the core pattern behind all AI agents — a loop that
# observes, thinks, acts, and remembers.


def research_round(question, memory):
    """Execute a single round of research.

    Parameters:
        question (str): What to research.
        memory (ResearchMemory): The shared memory object.
    """
    category = categorize_question(question)
    print(f"\n  Category: {category}")

    # --- Phase 1: Generate smart search terms ---
    print(f"\n  Generating search terms...")
    search_terms = generate_search_terms(question)

    # --- Phase 2: Search with each term and combine results ---
    all_results = []
    for term in search_terms:
        print(f"\n  Searching for: '{term}'")
        results = gather_results(term)
        all_results.extend(results)

    # --- CONCEPT: Deduplication ---
    # When searching multiple terms, we might get the same result twice.
    # We remove duplicates by checking URLs we've already seen.
    seen_urls = set()
    unique_results = []
    for result in all_results:
        if result["url"] not in seen_urls:
            seen_urls.add(result["url"])
            unique_results.append(result)

    all_results = unique_results

    # --- Phase 3: Show raw results ---
    display_results(all_results, category)

    # --- Phase 4: AI Analysis with memory ---
    # Even if no search results were found, we still ask the AI
    # to answer from its own knowledge. This way the agent is
    # always useful, even when APIs return nothing.
    analysis = analyze_with_ai(question, all_results, category, memory)
    if analysis:
        display_analysis(analysis)

    # --- Phase 5: Store in memory ---
    memory.add_round(question, category, all_results, analysis)


def main():
    """Run the research agent loop."""
    greet_user()

    # --- CONCEPT: Creating an Object from a Class ---
    # This creates a new ResearchMemory object. It's like filling
    # out the blueprint — now 'memory' is a real thing we can use.
    memory = ResearchMemory()

    # --- CONCEPT: While Loop ---
    # A 'while True' loop runs forever until we explicitly 'break' out.
    # This is what makes our agent persistent — it keeps asking
    # for questions until the user says 'quit'.
    while True:
        print()
        question = get_question()

        if question is None:
            print("  Please enter a question, or type 'quit' to exit.")
            continue

        # --- CONCEPT: Command Handling ---
        # Check for special commands before treating input as a question.
        command = question.lower().strip()

        if command in ("quit", "exit", "q"):
            print(f"\n  Goodbye! Completed {memory.get_round_count()} research round(s).")
            break

        if command == "history":
            display_history(memory)
            continue

        # --- Run a research round ---
        research_round(question, memory)

        print(f"\n  Research round {memory.get_round_count()} complete.")
        print("  Ask another question to dig deeper, or type 'quit' to exit.")


if __name__ == "__main__":
    main()
