# Research Agent - Step 1: Python Basics
# =========================================
# This is our starting point. We'll grow this into a full AI research agent!

# --- CONCEPT: Variables ---
# Variables store information. Think of them as labeled boxes.
agent_name = "ResearchBot"
version = 1.0

# --- CONCEPT: Strings ---
# Text in Python is called a "string". You wrap it in quotes.
greeting = f"Hello! I'm {agent_name} v{version}."

# --- CONCEPT: Print ---
# print() displays text on the screen. It's how your program talks to you.
print(greeting)
print("I'm a research assistant that helps find answers to your questions.")
print()

# --- CONCEPT: Input ---
# input() asks the user to type something. It waits for them to press Enter.
question = input("What would you like to research? ")

# --- CONCEPT: If/Else (Making Decisions) ---
# Your program can make choices based on conditions.
if question == "":
    print("You didn't enter a question! Try again next time.")
else:
    print(f"\nGreat question: '{question}'")
    print("I can't search for answers yet, but I will soon!")

# --- CONCEPT: Lists ---
# Lists hold multiple items, like a to-do list.
steps_to_learn = [
    "Python basics (YOU ARE HERE!)",
    "Functions and organization",
    "Working with APIs",
    "Web search integration",
    "AI-powered reasoning",
    "Agent loops and memory",
]

print("\n--- My Learning Roadmap ---")

# --- CONCEPT: Loops ---
# A 'for' loop repeats an action for each item in a list.
for step_number, step in enumerate(steps_to_learn, start=1):
    print(f"  Step {step_number}: {step}")

print("\nMore features coming soon!")
