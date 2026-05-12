"""
Project: Keyword Extractor
What it does: Extracts the most important keywords and phrases from text.
Uses TF-IDF (Term Frequency-Inverse Document Frequency) concept simplified:
  - Words that appear OFTEN in one document but RARELY in general English
    are likely important keywords for that specific document.

Run: python 33_keyword_extractor.py
Run: python 33_keyword_extractor.py --file article.txt --top 15
"""

import re
import os
import argparse
import math
from collections import Counter


SAMPLE_TEXT = """
Machine learning is a subset of artificial intelligence that focuses on
developing algorithms that allow computers to learn from data. Instead of
being explicitly programmed for every task, machine learning algorithms
improve their performance through experience.

Deep learning, a subset of machine learning, uses neural networks with
many layers to model complex patterns in data. These neural networks are
inspired by the structure of the human brain and consist of interconnected
nodes called neurons.

Supervised learning involves training a model on labeled data, where the
correct output is provided for each training example. The model learns to
map inputs to outputs. Unsupervised learning, on the other hand, works with
unlabeled data and discovers hidden patterns or structures on its own.

Natural language processing (NLP) is a branch of artificial intelligence
that deals with the interaction between computers and human language.
Applications of NLP include machine translation, sentiment analysis,
speech recognition, and text generation. Large language models like GPT
and BERT have revolutionized the field of natural language processing.
"""

# Common English words that carry little meaning (stop words)
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "that", "this", "these", "those", "it", "its", "they", "their",
    "we", "our", "you", "your", "he", "she", "him", "her", "as", "not", "no",
    "can", "if", "then", "than", "each", "every", "all", "more", "most",
    "very", "just", "also", "into", "through", "between", "which", "who",
    "how", "where", "when", "what", "why", "about", "after", "before", "up",
    "down", "out", "many", "such", "other", "both", "own", "during", "while",
    "however", "therefore", "although", "instead",
}

# Common English word frequencies (simplified IDF reference)
# Words that appear in many documents have lower IDF scores
COMMON_ENGLISH_WORDS = {
    "learn", "make", "work", "use", "way", "time", "go", "come",
    "give", "take", "get", "know", "think", "see", "look", "need",
    "people", "world", "place", "system", "process", "example", "type",
    "different", "important", "based", "called", "allows", "involves",
}


def extract_words(text):
    """Extract and normalize words from text."""
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    # Filter out stop words and very short words
    return [w for w in words if w not in STOP_WORDS and len(w) > 3]


def compute_tf(words):
    """
    Term Frequency (TF): how often each word appears in this document.
    TF = count / total_words (normalized so longer documents don't have unfair advantage)
    """
    total    = len(words)
    counts   = Counter(words)
    # Divide each count by total to get a fraction
    return {word: count / total for word, count in counts.items()}


def compute_idf_score(word):
    """
    Simplified Inverse Document Frequency (IDF).
    In a real IDF, we'd measure how many documents a word appears in.
    Here we use a simplified version: penalize common English words.

    IDF is high for rare/domain-specific words → more important as keywords
    IDF is low for common words → less important as keywords
    """
    if word in COMMON_ENGLISH_WORDS:
        return 0.5   # common words get a lower score
    elif len(word) >= 8:
        return 2.0   # longer words tend to be more specific/technical
    else:
        return 1.0   # neutral score for regular words


def extract_keywords(text, top_n=10):
    """
    Extract top keywords using a simplified TF-IDF approach.
    Returns a list of (word, score) tuples sorted by score descending.
    """
    words  = extract_words(text)
    tf     = compute_tf(words)

    # Compute TF-IDF score for each word
    # TF-IDF = TF × IDF — words frequent in THIS doc but rare in general
    scores = {}
    for word, tf_score in tf.items():
        idf_score     = compute_idf_score(word)
        scores[word]  = tf_score * idf_score

    # Sort by score, highest first
    sorted_keywords = sorted(scores.items(), key=lambda x: -x[1])
    return sorted_keywords[:top_n]


def extract_bigrams(words, top_n=5):
    """
    Extract two-word phrases (bigrams) that commonly appear together.
    e.g., "machine learning", "neural networks", "deep learning"
    Bigrams often capture concepts better than single words.
    """
    filtered = extract_words(" ".join(words) if isinstance(words, list) else words)

    # Create bigrams by pairing consecutive words
    bigrams = [(filtered[i], filtered[i+1])
               for i in range(len(filtered) - 1)]

    # Count bigram frequencies
    bigram_counts = Counter(bigrams)

    # Filter to only meaningful bigrams (not stop words in either position)
    meaningful = {bg: cnt for bg, cnt in bigram_counts.items()
                  if cnt >= 2}  # must appear at least twice

    return Counter(meaningful).most_common(top_n)


def print_keyword_report(text, top_n):
    """Display the keyword extraction results."""
    words    = extract_words(text)
    keywords = extract_keywords(text, top_n)
    bigrams  = extract_bigrams(words, top_n=5)

    print(f"\n  Total words (excluding stop words): {len(words)}")
    print(f"  Unique words: {len(set(words))}")

    print(f"\n  Top {top_n} Keywords (by TF-IDF score):")
    print(f"  {'RANK':>5}  {'KEYWORD':<25}  {'SCORE':>8}  {'BAR'}")
    print("  " + "─" * 65)

    max_score = keywords[0][1] if keywords else 1
    for rank, (word, score) in enumerate(keywords, 1):
        bar_len = int(score / max_score * 25)
        bar     = "█" * bar_len
        print(f"  {rank:>5}. {word:<25}  {score:>8.5f}  {bar}")

    if bigrams:
        print(f"\n  Top Phrases (bigrams appearing ≥ 2 times):")
        for phrase, count in bigrams:
            phrase_str = f"{phrase[0]} {phrase[1]}"
            print(f"    '{phrase_str}'  — {count} times")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Extract keywords from text")
parser.add_argument("--file", help="Text file to analyze")
parser.add_argument("--top",  type=int, default=10, help="Number of keywords to show")
args = parser.parse_args()

print("=== Keyword Extractor ===\n")

if args.file and os.path.exists(args.file):
    with open(args.file) as f:
        text = f.read()
    print(f"Analyzing: {args.file}\n")
else:
    print("Using built-in sample text about Machine Learning.\n")
    text = SAMPLE_TEXT

print_keyword_report(text, args.top)
