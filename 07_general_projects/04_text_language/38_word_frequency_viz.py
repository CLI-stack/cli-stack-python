"""
Project: Word Frequency Visualizer
What it does: Analyzes word frequencies in text and creates visualizations.
Shows which words are most common using bar charts and a text-based word cloud.
Useful for understanding the key topics in a document.

Install: pip install matplotlib (for bar chart)
Run: python 38_word_frequency_viz.py
Run: python 38_word_frequency_viz.py --file document.txt --top 20
"""

import re
import os
import argparse
from collections import Counter

SAMPLE_TEXT = """
Python is an interpreted high-level general-purpose programming language.
Python's design philosophy emphasizes code readability, and its language
constructs aim to help programmers write clear, logical code for small and
large-scale projects. Python is dynamically typed and garbage-collected.
It supports multiple programming paradigms, including structured, object-oriented
and functional programming. Python is often described as a batteries included
language due to its comprehensive standard library.

Python was created by Guido van Rossum and first released in 1991. In 2000,
Python 2.0 was released. Python 3.0 was released in 2008. Python 3 was
designed to rectify certain design flaws in the language. Python consistently
ranks as one of the most popular programming languages. Python is widely used
in scientific computing, data analysis, machine learning, web development,
and systems scripting. Python developers are in high demand worldwide.
"""

STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","have","has","had",
    "do","does","did","will","would","could","should","that","this","it",
    "its","as","not","than","like","about","after","before","often","among",
    "while","also","both","such","due","its","were","been","he","she","his",
    "her","they","their","we","our","i","you","your","my","which","who",
    "into","within","without","including","designed","released","created",
}


def count_words(text, min_length=3):
    """Count word frequencies, excluding stop words and short words."""
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    # Keep only words that:
    # 1. Are not stop words
    # 2. Are at least min_length characters
    meaningful = [w for w in words
                  if w not in STOP_WORDS and len(w) >= min_length]
    return Counter(meaningful)


def text_bar_chart(word_counts, top_n=15):
    """Print a horizontal bar chart of word frequencies using ASCII characters."""
    top    = word_counts.most_common(top_n)
    max_ct = top[0][1] if top else 1
    bar_w  = 40  # max bar width in characters

    print(f"\n  Word Frequency Chart (top {top_n}):\n")
    print(f"  {'WORD':<20} {'COUNT':>5}  FREQUENCY BAR")
    print("  " + "─" * 65)

    for word, count in top:
        bar_len = int(bar_w * count / max_ct)
        bar     = "█" * bar_len

        # Color-code by frequency
        if count == max_ct:
            color = "\033[93m"   # gold for top word
        elif count >= max_ct * 0.6:
            color = "\033[92m"   # green for frequent
        else:
            color = "\033[36m"   # cyan for less frequent
        RST = "\033[0m"

        print(f"  {word:<20} {count:>5}  {color}{bar}{RST} {count}")


def text_word_cloud(word_counts, top_n=30, width=60):
    """
    Generate a simple text-based word cloud.
    More frequent words appear larger (by repeating the word).
    In a real word cloud, font size represents frequency.
    Here we repeat words to simulate different sizes.
    """
    top     = word_counts.most_common(top_n)
    max_ct  = top[0][1] if top else 1

    print(f"\n  Text Word Cloud (top {top_n} words):\n")
    print("  " + "─" * width)

    # Build word cloud content with size proportional to frequency
    cloud_words = []
    for word, count in top:
        # Repeat the word proportionally to its frequency
        size = max(1, int(count / max_ct * 3))
        cloud_words.extend([word.upper() if size == 3 else word] * size)

    import random
    random.shuffle(cloud_words)

    # Wrap into lines
    line    = "  "
    for word in cloud_words:
        if len(line) + len(word) + 1 > width:
            print(line)
            line = "  " + word + "  "
        else:
            line += word + "  "
    if line.strip():
        print(line)

    print("  " + "─" * width)


def matplotlib_chart(word_counts, top_n=15):
    """Create a proper bar chart using matplotlib."""
    try:
        import matplotlib.pyplot as plt

        top    = word_counts.most_common(top_n)
        words  = [w for w, _ in top]
        counts = [c for _, c in top]

        # Create horizontal bar chart (easier to read word labels)
        plt.figure(figsize=(10, 6))
        bars = plt.barh(words[::-1], counts[::-1], color="steelblue")  # reverse for top-to-bottom

        # Add count labels inside bars
        for bar, count in zip(bars, counts[::-1]):
            plt.text(bar.get_width() / 2, bar.get_y() + bar.get_height()/2,
                     str(count), va="center", ha="center", color="white", fontweight="bold")

        plt.title(f"Top {top_n} Most Frequent Words")
        plt.xlabel("Frequency")
        plt.tight_layout()
        plt.savefig("word_frequency.png")
        plt.close()
        print(f"\n  Bar chart saved: word_frequency.png")

        import os
        os.remove("word_frequency.png")

    except ImportError:
        print("\n  (matplotlib not available — install with: pip install matplotlib)")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Visualize word frequencies in text")
parser.add_argument("--file", help="Text file to analyze")
parser.add_argument("--top",  type=int, default=15, help="Top N words to show")
args = parser.parse_args()

print("=== Word Frequency Visualizer ===\n")

if args.file and os.path.exists(args.file):
    with open(args.file) as f:
        text = f.read()
    print(f"Analyzing: {args.file}")
else:
    print("Using built-in sample text about Python.\n")
    text = SAMPLE_TEXT

word_counts = count_words(text)

print(f"  Total unique words (after filtering): {len(word_counts)}")
print(f"  Most common: {word_counts.most_common(3)}")

# Show text-based visualizations (no install needed)
text_bar_chart(word_counts, top_n=args.top)
text_word_cloud(word_counts, top_n=25)

# Show matplotlib chart if available
matplotlib_chart(word_counts, top_n=args.top)
