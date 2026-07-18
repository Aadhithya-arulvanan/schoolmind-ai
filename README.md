# SchoolMind AI

An AI-powered school data assistant. Admins, teachers, and parents ask
questions in plain language (English or a regional language) about
attendance, fees, marks, and at-risk students — instead of digging through
spreadsheets — and get back a direct answer, a conversational summary, or a
downloadable PDF report.

Built with Streamlit, Gemini, SQLite, and ChromaDB.

## Why this exists

School admin data (attendance, fees, marks) is usually locked in
spreadsheets that only make sense to whoever built them. SchoolMind AI puts
a single natural-language interface in front of that data, with:

- **Role-based access** — Principal/Teacher see everything, Parents only
  ever see their own child's data.
- **A hybrid retrieval architecture** — structured questions ("who has
  pending fees over ₹30,000") are answered with real SQL, not a vector
  search; only unstructured lookups (building a report/summary for one
  student) use semantic retrieval.
- **Multilingual support** — ask and receive answers in Hindi, Tamil,
  Telugu, Malayalam, Kannada, French, German, or Spanish.
- **Risk flagging** — automatically surfaces students who are falling
  behind on attendance, fees, or marks, without anyone having to
  cross-reference three spreadsheets by hand.

## Architecture

```
                    Question
                       |
                       v
              Intent Classifier
              (local_intent.py)
                       |
        +--------------+--------------+
        |                             |
   Structured                   Unstructured
  (marks/fees/attendance/        (report / summary
   risk_analysis)                 for one student)
        |                             |
        v                             v
   SQLite (schoolmind.db)        ChromaDB (chroma_db/)
   analytics.py                  chroma_tools.py
        |                             |
        +--------------+--------------+
                       |
                       v
              Prompt Assembly
              (schoolmind_ai.py)
                       |
                       v
                    Gemini
                       |
                       v
          Answer / Summary / PDF Report
          (+ translation pass if a
           non-English language was
           detected in the question)
```

See **[PROMPTS.md](./PROMPTS.md)** for the full reasoning behind the
chunking strategy, retrieval design, and the exact prompts (including the
anti-hallucination guardrails) sent to Gemini.

## Tech stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Structured data | SQLite (`db.py`) |
| Unstructured/semantic retrieval | ChromaDB |
| LLM | Google Gemini (`google-generativeai`) |
| PDF generation | ReportLab |
| Language detection | Rule-based keyword matching (`translator.py`) |

## Project structure

```
schoolmind-ai/
├── app.py                 # Streamlit entrypoint: login gate + UI
├── auth.py                # Hardcoded users & roles (Principal/Teacher/Parent)
├── db.py                  # SQLite schema + CSV -> SQLite migration
├── load_all_data.py       # Populates ChromaDB from SQLite (chunking logic)
├── local_intent.py        # Rule-based intent classifier
├── local_name.py          # Extracts a student name from a question (queries SQLite)
├── analytics.py           # All structured (SQL) queries for the dashboard & Q&A
├── chroma_tools.py        # Semantic retrieval + exact-match re-check
├── schoolmind_ai.py        # Routes intent -> SQL or vector retrieval -> Gemini prompt
├── translator.py          # Rule-based language detection
├── report_generator.py    # Builds the downloadable PDF report
├── data/                  # Original CSVs (kept for reference/migration; SQLite is now the source of truth)
├── PROMPTS.md              # Prompt design & chunking rationale
└── requirements.txt
```

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/Aadhithya-arulvanan/schoolmind-ai.git
   cd schoolmind-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Gemini API key as an environment variable** — never commit it
   to the repo:
   ```bash
   export GEMINI_API_KEY="your-key-here"        # macOS/Linux
   setx GEMINI_API_KEY "your-key-here"           # Windows
   ```
   `schoolmind_ai.py` should read this via `os.getenv("GEMINI_API_KEY")`.

4. **Run the app**
   ```bash
   streamlit run app.py
   ```
   On first run, `app.py` automatically migrates `data/*.csv` into
   `schoolmind.db` and loads `chroma_db/` if either doesn't exist yet.

## Logging in

Access is role-based. There is no self-registration — accounts are defined
in `auth.py`.

| Role        | Username                                             | Password                                     |
|-------------|------------------------------------------------------|----------------------------------------------|
| Principal   | `principal`                                          | `principal123`                               |
| Teacher     | `teacher`                                            | `teacher123`                                 |
| Parent      | student's full name, lowercase (e.g. `aarav sharma`) | `<Student Name>123` (e.g. `Aarav Sharma123`) |

Principal and Teacher see full school-wide dashboard stats and can ask any
question. Parent accounts only see their own linked child and are
restricted to marks/fees/attendance/summary/report questions about that
child — anything else, or any other student's name, is blocked.

> These are demo credentials for a portfolio project — hardcoded, plaintext
> passwords are not a production pattern. A real deployment would hash
> passwords and store users in a `users` table rather than in source code.

## Example questions

- "Who has attendance below 75%?"
- "What are Aarav Sharma's marks in maths?"
- "Show me students who are at risk"
- "Generate a report for Priya Sharma"
- "Fees remaining for Vihaan Gupta"
- "Aarav Sharma ka summary batao hindi mein" *(multilingual)*

## Known limitations

- Hardcoded demo credentials (see above).
- Intent and language detection are keyword-based, so unusual phrasing can
  fall through to "unknown" — see `PROMPTS.md` for the reasoning and
  possible follow-ups.
- Designed and tested against ~50 students; SQL layer would need
  pagination/indexing review at real-school scale.