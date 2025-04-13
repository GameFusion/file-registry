# file-registry
Python-based file registry system for cataloging and searching files across storage locations with metadata and AI analysis capabilities.

# File Registry

A Python-based file registry system for cataloging and searching files across storage locations with metadata and AI analysis capabilities.

## Overview

File Registry helps you build and maintain a central database of file information across your storage volumes. It indexes file metadata including paths, names, sizes, and MD5 hashes, enabling fast searches and analysis across distributed storage systems.

### Key Features

- **Fast File Search**: Quickly locate files by name, path, or hash across multiple storage units and servers
- **MD5 Hash Computation**: Generate and store MD5 hashes for file integrity and duplicate detection
- **Metadata Framework**: Extensible system for adding custom metadata and AI-generated metadata to files
- **Large-Scale Support**: Optimized for handling millions of files across distributed storage
- **Configurable Scanning**: Control which directories and file types to include/exclude from scanning

## Use Cases

- **Content Management**: Find and organize files across multiple storage locations
- **Data Preparation**: Catalog and prepare data for AI analysis and machine learning
- **Storage Optimization**: Identify duplicates and analyze storage patterns 
- **Digital Asset Management**: Track and manage large collections of digital assets

## Installation

### Clone Repository
```bash
# Clone the repository
git clone https://github.com/GameFusion/file-registry.git
cd file-registry
```
### Installation Using a Virtual Environment (Optional but recommended)
```bash
# Optional: Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```
### Installation Requirements
```bash
# Install required packages (either method works)
pip install -r requirements.txt
# Or install directly:
# pip install mysql-connector-python
```
### Run the Setup Wizard
```bash
# Run the setup script to configure your environment
python setup.py
```

The setup script will guide you through:
1. Creating necessary configuration files
2. Setting up database connection credentials
3. Creating database tables
4. Configuring excluded files and directories

## Configuration

The system uses JSON configuration files (stored in the `config` directory):

1. `credentials.json` - Database connection details
2. `excluded_files.json` - Files to exclude from scanning
3. `excluded_dirs.json` - Directories to exclude from scanning

These files are created automatically by the setup script (setup.py), but can be modified manually as needed.

## Usage

### Scanning Files

```bash
python file_registry_scan.py /path/to/scan
```

### Searching Files

```bash
python file_registry_search.py "search_term"
```

### Viewing Logs

```bash
python file_registry_log.py
```

### MD5 Metadata Scanner

```bash
python md5_metadata_scanner.py /path/to/scan
```

## How to Use

```bash
# Store MD5s and file metadata to database (default)
python md5_metadata_scanner.py /path/to/scan

# Store MD5s as extended attributes (Linux)
python md5_metadata_scanner.py /path/to/scan --storage xattr

# Store MD5s in both database and extended attributes
python md5_metadata_scanner.py /path/to/scan --storage both

# Enable verbose output to see details of each file
python md5_metadata_scanner.py /path/to/scan -v
```

## Project Structure

- `file_registry_scan.py` - Main script for scanning and adding files to the database
- `file_registry_search.py` - Search for files in the database registry
- `file_registry_log.py` - Display log information
- `md5_metadata_scanner.py` - Compute and store MD5 hashes for files

## Performance Optimizations

The system includes several optimizations for handling large file systems:
- Caching mechanism to speed up repeated operations
- Exclusion of system directories like `.snapshot`, `.git`, and `.gitold`
- Connection validation to ensure database reliability
- Warm-up phase optimization for faster startup

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Authors

- **Andreas Carlen** - *Initial work* - [GitHub](https://github.com/gamefusion)


