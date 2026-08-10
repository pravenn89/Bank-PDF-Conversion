# Bank Statement Converter Workflow & Git Push Guidelines

## 1. New Bank Statement Parser Integration Checklist
Whenever adding or modifying a bank statement parser format:
- Update `parser.py` with the parser implementation and auto-detection routing.
- Add corresponding test cases in `test_parser.py` and run unittests to verify pass rate.
- **Automatically update the Supported Banks sidebar list in `streamlit_app.py`** and the upload zone subtext in `templates/index.html` to include the newly supported bank name.
- Generate the converted `.xlsx` spreadsheet for the user.

## 2. Auto Git Commit and Push Guidelines
Whenever modifying, creating, or refactoring code or project files in a repository:
1. Verify that changes build and pass unit tests.
2. Automatically stage all modified/new files using `git add`.
3. Create a descriptive commit message summarizing the changes (`git commit -m "..."`).
4. Automatically push the commit(s) to the remote GitHub repository (`git push origin <branch>`).
