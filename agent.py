# Research Agent - Step 2: Functions
# ====================================
# Functions let you group code into reusable blocks.
# Think of them as "recipes" — you define them once, then call them anytime.

# --- CONCEPT: Functions ---
# 'def' defines a function. The name describes what it does.
# Parameters (in parentheses) are inputs the function accepts.
# 'return' sends a result back to whoever called the function.


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
    """Ask the user for a research question and return it.

    Returns:
        str: The user's question, or None if they didn't type anything.
    """
    question = input("What would you like to research? ")

    # .strip() removes extra spaces from the start and end
    question = question.strip()

    if question == "":
        return None
    return question


def categorize_question(question):
    """Figure out what type of research the user wants.

    This is a simple version — later we'll use AI to do this.

    Parameters:
        question (str): The user's research question.

    Returns:
        str: The category of research.
    """
    # .lower() converts text to lowercase so we can match more easily
    question_lower = question.lower()

    # --- CONCEPT: Dictionaries ---
    # A dictionary maps "keys" to "values", like a real dictionary
    # maps words to definitions. Here we map keywords to categories.
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

    # Check if any keyword appears in the question
    for keyword, category in categories.items():
        if keyword in question_lower:
            return category

    # Default if no keywords match
    return "General Business Research"


def plan_research(question, category):
    """Create a research plan based on the question and category.

    Parameters:
        question (str): The user's research question.
        category (str): The type of research identified.

    Returns:
        dict: A research plan with sources and steps.
    """
    # --- CONCEPT: Dictionaries (deeper) ---
    # Dictionaries can hold any type of value, including lists and other dicts.
    plan = {
        "question": question,
        "category": category,
        "sources": ["Web Search", "News APIs", "Academic Papers"],
        "output_types": [
            "Summary",
            "Sources & Links",
            "Viewpoint Comparison",
            "Action Plan",
        ],
        "steps": [
            f"Search the web for: {question}",
            "Gather articles from news sources",
            "Look for relevant academic research",
            "Summarize key findings",
            "Compare different viewpoints",
            "Create an action plan",
        ],
    }
    return plan


def display_plan(plan):
    """Show the research plan to the user.

    Parameters:
        plan (dict): The research plan dictionary.
    """
    print(f"\n{'─' * 50}")
    print(f"  Research Category: {plan['category']}")
    print(f"{'─' * 50}")

    print(f"\n  Question: {plan['question']}")

    print("\n  Sources I'll check:")
    for source in plan["sources"]:
        print(f"    • {source}")

    print("\n  Research steps:")
    for i, step in enumerate(plan["steps"], start=1):
        print(f"    {i}. {step}")

    print("\n  You'll receive:")
    for output in plan["output_types"]:
        print(f"    ✓ {output}")

    print(f"\n{'─' * 50}")
    print("  ⚡ Search functionality coming in Step 3!")
    print(f"{'─' * 50}")


# --- CONCEPT: Main Function ---
# It's good practice to put your "starting point" in a main() function.
# This keeps everything organized and clear.

def main():
    """Run the research agent."""
    greet_user()

    question = get_question()

    if question is None:
        print("No question entered. Goodbye!")
        return

    category = categorize_question(question)
    plan = plan_research(question, category)
    display_plan(plan)


# --- CONCEPT: Entry Point ---
# This line means: "Only run main() if this file is executed directly."
# It won't run if this file is imported by another file.
if __name__ == "__main__":
    main()
