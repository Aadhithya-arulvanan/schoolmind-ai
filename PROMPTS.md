# Prompt & Retrieval Design

This document explains the RAG design decisions in SchoolMind AI: how data is
chunked, how retrieval is routed, and the exact prompts sent to Gemini —
including the guardrails that stop it from hallucinating.

## 1. Hybrid retrieval: SQL vs. vector search

A common RAG anti-pattern is running every question through a vector store,
even when the question is a structured lookup ("who has pending fees over
₹30,000"). SchoolMind AI avoids this by classifying intent first
(`local_intent.py`) and routing accordingly:

| Intent | Route | Why |
|---|---|---|
| `marks_query`, `fees_query`, `attendance_query`, `risk_analysis` | SQLite (`analytics.py`) | These are exact, structured, filterable/sortable questions. SQL gives exact, deterministic answers — a vector store would only return "similar" text, not a correct `WHERE`/`ORDER BY` result. |
| `student_summary`, `student_report` | ChromaDB (`chroma_tools.py`) | These need a bundle of one student's data pulled together as unstructured context to hand to the LLM for prose generation, not a single computed value. |

Intent classification itself (`local_intent.py`) is deliberately a simple
rule-based keyword matcher, not an LLM call. This is a conscious cost/speed
tradeoff: intent detection doesn't need language understanding, it needs to
be fast, free, and deterministic — every extra LLM call adds latency and
cost for something a keyword set already handles reliably enough for a
fixed-domain school assistant.

## 2. Chunking strategy

**Source of truth is SQLite** (`schoolmind.db`), not the CSVs. `load_all_data.py`
joins `students`, `attendance`, `fees`, and `marks` into one row per student,
then splits that row into **three separate chunks per student** — one each
for attendance, fees, and marks — before loading into ChromaDB.

**Why per-student, per-category chunks (not per-student single chunk, not
per-field):**
- A single combined chunk per student (attendance + fees + marks all in one
  document) would force every retrieval to pull irrelevant categories along
  with the relevant one, diluting the embedding and bloating the context
  sent to Gemini.
- Splitting further, to one chunk per individual field (e.g. a separate
  chunk just for "Maths: 78"), would fragment context too much — a report
  needs attendance/fees/marks as coherent blocks, not scattered numbers.
- Per-category-per-student is the middle ground: each chunk is a coherent,
  human-readable unit ("Type: Marks / Student: ... / Maths: ... / Science:
  ... / Total: ...") that can be retrieved and dropped straight into a
  report without extra assembly.

Each chunk carries `student_id` and `type` metadata, so future changes could
add metadata filtering. Currently, retrieval doesn't use that metadata for
filtering (see below).

## 3. Retrieval: semantic search + deterministic re-check

`chroma_tools.get_student_records(name)` does a semantic query against
Chroma for the student's name (`n_results=20`, generous on purpose to catch
all 3 chunk types for that student), **then filters the results again**,
keeping only chunks where the student's name literally appears in the text:

```python
for doc in results["documents"][0]:
    if name.lower() in doc.lower():
        filtered_docs.append(doc)
```

This second pass exists because vector similarity alone can surface a
different student with a similar-sounding name or similar numeric profile —
semantic search finds "close," not "correct." The exact-substring recheck
is a deterministic guardrail on top of a probabilistic retrieval step,
so a report is never built from the wrong student's data.

If no chunks match, `get_student_records` returns an empty list, and both
the report and summary prompts (below) treat that as "no data" and refuse
to generate rather than filling in placeholder content.

## 4. Language handling

`translator.py::detect_language` is also rule-based keyword matching
(checks for language names like "hindi", "tamil" in the question), not an
LLM call — same cost/latency reasoning as intent classification. If a
language is detected, the final answer is generated normally in English
first, then translated in a separate Gemini call (see prompt #4 below).
Doing generation and translation as two separate steps, rather than one
combined prompt, keeps the anti-hallucination rules focused only on the
generation step; translation is a much simpler, lower-risk task and is
kept isolated so a translation instruction can never dilute or override
the "don't invent data" rules.

## 5. The actual prompts

### 5a. Structured-answer prompt (SQL route)

Used for `marks_query` / `fees_query` / `attendance_query` / general
fallthrough questions, after SQL has already computed the answer set.

```
You are SchoolMind AI, a school data assistant.

Question:
{question}

Data (already filtered/sorted to answer this exact question — do not re-rank or recompute):
{context}

Rules:
1. Use ONLY the rows in "Data" above. Never use outside knowledge about
   students, schools, or typical academic performance.
2. Do not perform any additional ranking, sorting, or filtering — the data
   given is already the answer set.
3. If "Data" is empty or contains no rows, respond exactly with:
   "I couldn't find any records matching that question."
   Do not guess a plausible-sounding name or number.
4. State the answer in one or two plain sentences. Include the exact
   figure(s) from the data (do not round or approximate).
5. Do not mention SQL, databases, or how the data was retrieved.
```

**Design notes:** Rule 2 exists because the SQL layer already did the
sorting/filtering (`ORDER BY`, `LIMIT`, `WHERE`) — letting the LLM re-rank
in natural language risks it silently reordering based on the wrong column
or its own notion of "best." Rule 5 keeps implementation details out of
user-facing answers.

### 5b. Student report prompt (RAG route)

```
Create a professional student report using ONLY the data provided below.

Language: {report_language}

Student Data:
{context}

Rules:
- If "Student Data" above is empty or does not contain attendance, fee, or
  marks information, do NOT generate a report. Instead respond only with:
  "No records were found for this student — a report cannot be generated."
- Do not invent, estimate, or infer any number, grade, or attendance figure
  that is not explicitly present in the data above.
- If one category (e.g. Financial Status) is missing from the data but
  others are present, state "Data not available" for that section rather
  than guessing.

Include (only using sections supported by the data):
1. Student Profile
2. Academic Performance
3. Attendance
4. Financial Status
5. Overall Assessment
```

### 5c. Student summary prompt (RAG route)

Structurally identical to 5b, with "summary" swapped for "report" and no
PDF generation step afterward — used for quick conversational lookups
rather than a downloadable document.

### 5d. Translation prompt

```
You are a professional translator.

Translate EVERYTHING below into {language}.

Rules:
- Translate the complete text.
- Do not leave any English words.
- Do not add explanations.
- Do not add introductions.
- Do not ask questions.
- Return only the translated text.

TEXT:

{answer}
```

**Design note:** This runs only after the main answer/summary/report is
already generated in English, so mistranslation risk is isolated to
wording, never to facts — the numbers were already locked in by the earlier
anti-hallucination rules before translation ever sees them.

## 6. Known limitations (intentionally out of scope for this version)

- The `n_results=20` in Chroma retrieval is a fixed constant, not tuned or
  configurable — fine at 50 students, would need revisiting at a larger
  school size.
- Intent and language detection are keyword-based, so unusual phrasing
  (e.g. "how much did she get in maths" instead of "marks") can fall
  through to `unknown`. This is a precision/recall tradeoff acceptable for
  a fixed-domain demo; a production version might fall back to an LLM
  classifier only when keyword matching fails, to keep the fast path fast.
- Metadata filtering (`type`, `student_id` are already stored on every
  chunk) isn't used yet in `chroma_tools.py` — the exact-substring recheck
  is currently doing that job. Switching to a `where={"student_id": ...}`
  filter once a numeric ID is available (rather than matching on name text)
  would be a more robust follow-up.