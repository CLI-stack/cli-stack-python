"""
Project: Text Readability Scorer
What it does: Scores text using multiple readability formulas to assess
how easy it is to read. Useful for content writers, educators, and anyone
who needs to match text complexity to their audience.

Formulas used:
  - Flesch Reading Ease: 100=very easy, 0=very hard
  - Flesch-Kincaid Grade: US school grade level (6 = 6th grade)
  - Gunning Fog Index:    years of education needed to understand
  - SMOG Grade:           grades of education needed (based on polysyllable words)

Run: python 31_readability_scorer.py
Run: python 31_readability_scorer.py --file mytext.txt
"""

import re
import os
import argparse

SAMPLE_TEXTS = {
    "Simple (Children's Book)": """
The cat sat on the mat. The dog ran after the cat. The cat ran up the tree.
The dog barked at the tree. The cat looked down. The dog looked up.
They were friends but they liked to play this game every day.
""",
    "Medium (Newspaper)": """
Scientists at the University of Cambridge have discovered a new method
for treating bacterial infections using modified bacteriophages. The research,
published in Nature Medicine, demonstrates that engineered viruses can target
antibiotic-resistant bacteria with high precision. Clinical trials are expected
to begin within the next two years, pending regulatory approval.
""",
    "Complex (Academic Journal)": """
The epistemological ramifications of quantum decoherence necessitate a
fundamental reassessment of the ontological status of superposition states
within the Copenhagen interpretation framework. Macroscopic quantum phenomena,
while theoretically permissible, encounter phenomenological constraints
that preclude observable manifestation under standard thermodynamic conditions.
""",
}


def count_syllables(word):
    """Count syllables in a word using vowel-group counting heuristic."""
    word = re.sub(r"[^a-zA-Z]", "", word.lower())
    if not word:
        return 0

    count = 0
    prev_vowel = False
    vowels = "aeiouy"

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1   # new vowel group = new syllable
        prev_vowel = is_vowel

    # Silent 'e' at the end of a word
    if word.endswith("e") and count > 1:
        count -= 1

    return max(1, count)


def count_polysyllables(words):
    """Count words with 3 or more syllables (polysyllabic words)."""
    return sum(1 for w in words if count_syllables(w) >= 3)


def analyze_text(text):
    """Extract basic text metrics needed for all readability formulas."""
    # Extract words (alphabetic only)
    words = re.findall(r"\b[a-zA-Z]+\b", text)

    # Split into sentences (split at . ! ? followed by space or end)
    sentences = re.split(r"[.!?]+(?:\s|$)", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    word_count      = len(words)
    sentence_count  = max(len(sentences), 1)
    syllable_count  = sum(count_syllables(w) for w in words)
    poly_count      = count_polysyllables(words)

    return word_count, sentence_count, syllable_count, poly_count


def flesch_reading_ease(word_count, sentence_count, syllable_count):
    """
    Flesch Reading Ease (1948):
    Score = 206.835 − 1.015(W/S) − 84.6(Sy/W)
    Where: W = words, S = sentences, Sy = syllables

    90-100: Very Easy    (5th grade)
    70-80:  Fairly Easy  (6th grade)
    60-70:  Standard     (7th-8th grade)
    50-60:  Fairly Hard  (high school)
    30-50:  Difficult    (college)
    0-30:   Very Hard    (professional)
    """
    if word_count == 0 or sentence_count == 0:
        return 0
    score = (206.835
             - 1.015  * (word_count / sentence_count)
             - 84.6   * (syllable_count / word_count))
    return max(0, min(100, score))


def flesch_kincaid_grade(word_count, sentence_count, syllable_count):
    """
    Flesch-Kincaid Grade Level (1975):
    Grade = 0.39(W/S) + 11.8(Sy/W) − 15.59
    Outputs US school grade level: 6 = 6th grade, 12 = 12th grade
    """
    if word_count == 0 or sentence_count == 0:
        return 0
    grade = (0.39  * (word_count / sentence_count)
             + 11.8 * (syllable_count / word_count)
             - 15.59)
    return max(0, grade)


def gunning_fog(word_count, sentence_count, poly_count):
    """
    Gunning Fog Index (1952):
    Grade = 0.4 × ((W/S) + 100 × (Poly/W))
    Estimates years of formal education needed.
    17+ = college graduate level
    """
    if word_count == 0 or sentence_count == 0:
        return 0
    return 0.4 * ((word_count / sentence_count) + 100 * (poly_count / word_count))


def smog_grade(sentence_count, poly_count):
    """
    SMOG Grade (1969):
    Grade = 3 + √(polysyllable count × 30/sentence count)
    Highly accurate for health literacy materials.
    """
    import math
    if sentence_count == 0:
        return 0
    return 3 + math.sqrt(poly_count * (30 / sentence_count))


def print_readability_report(label, text):
    """Run all readability tests and print a formatted report."""
    GREEN = "\033[92m"
    YEL   = "\033[33m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    word_count, sentence_count, syllable_count, poly_count = analyze_text(text)

    flesch_ease  = flesch_reading_ease(word_count, sentence_count, syllable_count)
    fk_grade     = flesch_kincaid_grade(word_count, sentence_count, syllable_count)
    fog          = gunning_fog(word_count, sentence_count, poly_count)
    smog         = smog_grade(sentence_count, poly_count)

    # Determine audience level from Flesch score
    if flesch_ease >= 80:   audience = "Children / General public"
    elif flesch_ease >= 60: audience = "Adults / General readers"
    elif flesch_ease >= 40: audience = "Educated adults"
    else:                   audience = "Specialists / Academics"

    ease_color = GREEN if flesch_ease >= 60 else (YEL if flesch_ease >= 40 else RED)

    print(f"\n  ── {label} ──")
    print(f"  Words: {word_count}  |  Sentences: {sentence_count}  |  "
          f"Syllables: {syllable_count}  |  Polysyllables: {poly_count}")
    print()
    print(f"  {'Formula':<30} {'Score':>8}  Interpretation")
    print("  " + "─" * 65)
    print(f"  {'Flesch Reading Ease':<30} {ease_color}{flesch_ease:>7.1f}{RST}  "
          f"{'High=Easy, Low=Hard'}")
    print(f"  {'Flesch-Kincaid Grade':<30} {fk_grade:>7.1f}  Grade {fk_grade:.0f} level")
    print(f"  {'Gunning Fog Index':<30} {fog:>7.1f}  {fog:.0f} years education needed")
    print(f"  {'SMOG Grade':<30} {smog:>7.1f}  Grade {smog:.0f} level")
    print(f"\n  Target Audience: {audience}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Score text readability")
parser.add_argument("--file", help="Text file to analyze")
args = parser.parse_args()

print("=== Text Readability Scorer ===\n")

if args.file and os.path.exists(args.file):
    with open(args.file) as f:
        text = f.read()
    print_readability_report(os.path.basename(args.file), text)
else:
    # Run on all three sample texts to compare difficulty levels
    for label, text in SAMPLE_TEXTS.items():
        print_readability_report(label, text)
