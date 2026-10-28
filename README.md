
# 🎬 AI-Assisted Movie Recommendation System

A robust Python 3.12 command-line recommendation engine that analyzes movie metadata and user rating distributions to compute popularity metrics and generate personalized, genre-based recommendations.

---

## 💡 Overview & Architecture

This project implements a multi-tiered recommendation engine using modular Python routines and defensive data parsing. Designed as an AI-assisted software engineering project, the core logic was developed, audited, and verified using structured prompt engineering to meet strict production standards without relying on external third-party libraries.

### 🌟 Key Recommendation Features
1. **Movie Popularity Ranking**: Ranks top $N$ movies overall based on non-rounded average ratings with secondary alphabetical tie-breaking.
2. **Genre-Specific Popularity**: Computes top $N$ movies within any target genre using case-insensitive filtering.
3. **Genre Hierarchy Analysis**: Ranks overall genre popularity by computing the average of average movie ratings per genre.
4. **User Preference Profiling**: Identifies a user's top preferred genre by aggregating their historical rating averages.
5. **Personalized Recommendations**: Recommends up to 3 highest-rated, unrated movies from a user's most preferred genre.

---

## 🛠️ System Design & Defensive Data Handling

The pipeline reads raw pipe-delimited text files (`movie_genre|movie_id|movie_name` and `movie_name|rating|user_id`) with comprehensive edge-case protection:

```text
               ┌────────────────────────┐
               │    Raw Data Files      │
               │ (movies.txt, ratings)  │
               └───────────┬────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │   Data Normalization & Loader    │
          │  - Case-folding & Whitespace strip│
          │  - Range Validation [0.0 - 5.0]  │
          │  - Duplicate & Malformed Filtering│
          └────────────────┬─────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │     Recommendation Engine        │
          │  - Movie/Genre Average Ratings   │
          │  - User Profile Aggregations     │
          │  - Unrated Item Filter & Ranker  │
          └────────────────┬─────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │     CLI & Automated Testing      │
          │   (Interactive Menu & Test Suite)│
          └──────────────────────────────────┘
```

### 🛡️ Defensive Engineering Features
* **Case-Insensitive Matching**: Uses Unicode case-folding (`.casefold()`) to match titles, user IDs, and genres robustly across input files without altering original display names.
* **Malformed Line Skipping**: Rejects records with missing fields, non-numeric values, or ratings outside the inclusive $[0.0, 5.0]$ range.
* **Integrity Validation**: Filters out duplicate rating entries by the same user for the same movie, as well as ratings referencing unknown movie titles.
* **Warning Logger**: Captures line-by-line parsing warnings without halting execution or throwing uncaught exceptions.

---

## 🧪 Automated Testing Pipeline

The project includes an automated test runner (`test_movie_recommender.py`) that utilizes Python's `tempfile` and `pathlib` modules to execute isolated unit and integration tests at runtime without cluttering the repository with permanent static test datasets.

```text
Loaded movie count:           PASS
Loaded rating count:          PASS
Movie warnings present:       PASS
Rating warnings present:      PASS
Top 3 movies ranking:         PASS
Top 3 Action movies ranking:  PASS
Top 3 genres ranking:         PASS
User preferred genre lookup:  PASS
Recommendations for user:     PASS
Unknown user handling:        PASS

Summary: Passed 10 of 10 checks.
```

---

## 🤖 AI-Assisted Engineering Workflow

This application was engineered using **ChatGPT (OpenAI)** under a structured AI-assisted development methodology:
* **Prompt Strategy**: Prompts were structured with explicit algorithmic requirements, strict input validation constraints, and Python 3.12 type hinting specifications.
* **Verification & Audit**: All AI-generated code, docstrings, and test scripts were manually code-reviewed for correct time complexity, dictionary data structure utilization, and sorting tie-breakers.
* **Documentation**: Detailed logs of prompts, case-sensitivity analysis, defensive measures, and testing paths are maintained in `coding_doc.pdf` and `testing_doc.pdf`.

---

## 📁 Repository Structure

```text
.
├── movie_recommender.py       # Primary CLI application & recommendation engine
├── test_movie_recommender.py  # Automated test suite with dynamic temp-file generation
├── coding_doc.pdf             # Prompt documentation & AI code audit report
├── testing_doc.pdf            # Test coverage analysis & input distribution documentation
└── README.md                  # Project overview & usage instructions
```

---

## 🚀 Usage Instructions

### Prerequisites
* **Python 3.12+** (No external dependencies required; uses Python standard library).

### Running the Interactive CLI
Launch the menu-driven application:
```bash
python3 movie_recommender.py
```

### Running the Automated Test Suite
Execute the dynamic test suite to verify core functions and data validation rules:
```bash
python3 test_movie_recommender.py
```
