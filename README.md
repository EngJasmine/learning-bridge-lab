# Learning Bridge Lab — Grade-Band Redesign

This version rebuilds the app around grade bands rather than reusing one generic activity structure for every child.

## Grade bands

- **Kindergarten**: Math, Reading, Science Reading, Social Studies, Character. No Writing subject is shown for Kindergarten.
- **Grades 2-3**: Math, Reading, Science Reading, Writing, Social Studies, Character.
- **Grades 4-5**: Math, Reading, Science Reading, Writing, Social Studies, Character.
- **Grade 6**: Math, Reading, Science Reading, Writing, Social Studies, Character.

## Content

The app includes 92 original activities:

- 4 activities per subject per grade band.
- Kindergarten excludes Writing by design.
- No Arabic subject is included in this version.
- The content is original and inspired by grade-appropriate workbook/Spectrum-style practice patterns, Ohio-style skill progressions, and teacher-designed activity formats.

## Design changes

- Filters are at the top so students reach the activity quickly.
- Question text is smaller and clearer than earlier versions.
- Math visuals only appear when they directly support the question.
- Reading and content-area passages use passage cards and evidence-based questions.
- Writing uses grade-appropriate organizers and checklists.
- Character activities use scenario decisions.
- The **Another activity** button picks a different activity from the selected grade/subject.

## Clean database

The package does not include an old database. When you run the app, it creates:

```text
learning_bridge_lab_progress_v3_clean.db
```

The Teacher Dashboard includes a reset button to clear local progress.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

For Streamlit Cloud, use `streamlit_app.py` as the entry point.
