# To publish to PyPI

1. Do the necessary changes
2. Change the version number on setup.py
3. Run `python -m build`
4. Run `twine upload --skip-existing dist/*`

Make sure to push to the GitHub repository before publishing to PyPI.

