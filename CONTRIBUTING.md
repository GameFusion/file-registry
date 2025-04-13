Contributing to File Registry
Thank you for your interest in contributing to File Registry! This document provides guidelines and instructions for contributing to this project.
Code of Conduct
By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.
How to Contribute
Reporting Bugs
If you find a bug, please create an issue with the following information:
Clear and descriptive title
Detailed steps to reproduce the bug
Expected behavior vs. actual behavior
System information (OS, Python version, database type and version)
Any relevant logs or error messages
Suggesting Enhancements
We welcome suggestions for new features or improvements. To suggest an enhancement:
Create an issue with a clear title describing the enhancement
Provide a detailed description of the proposed functionality
Explain why this enhancement would be useful
Include examples of how the feature would be used
Pull Requests
To submit code changes:
Fork the repository
Create a new branch for your changes
Make your changes with clear commit messages
Ensure your code follows the project's style and standards
Test your changes thoroughly
Submit a pull request with a clear description of the changes
Pull Request Process
Ensure your code follows Python best practices (PEP 8)
Update the README.md with details of any changes to the interface or functionality
Include necessary updates to documentation
The pull request will be reviewed by project maintainers
Development Setup
Prerequisites
Python 3.6 or higher
MySQL/MariaDB database
Required Python packages: mysql-connector-python, pyxattr (optional, for extended attribute support)
Setting Up Your Development Environment
Clone your fork of the repository
git clone https://github.com/yourusername/file-registry.git
cd file-registry

Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Create a local database for testing
mysql -u root -p
CREATE DATABASE file_registry_test;
EXIT;

Run the database setup script
mysql -u root -p file_registry_test < db_setup.sql

Create a config directory with your test configuration files
mkdir -p config
# Create credentials.json, excluded_dirs.json, and excluded_files.json

Coding Standards
Follow PEP 8 for Python code style
Include docstrings for all functions and classes
Write clear, descriptive commit messages
Add comments for complex logic
Write tests for new functionality
Testing
Before submitting a pull request, ensure all tests pass:
Run the test suite
python -m unittest discover tests

Test your changes with real data (if applicable)
python md5_metadata_scanner.py /path/to/test/directory
python file_registry.py /path/to/test/directory

Documentation
If you add new features or make significant changes, please update the documentation:
Update the README.md as necessary
Add or update docstrings
Update command-line help text
License
By contributing to File Registry, you agree that your contributions will be licensed under the project's MIT License.
Questions?
If you have any questions about contributing, please create an issue with your question.
Thank you for contributing to File Registry!