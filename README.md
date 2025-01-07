# Slack Space Manager

This tool provides advanced operations on the slack space of files, enabling users to work with individual files, perform system-wide slack space maintenance, and securely store and recover files using slack space.

## Features

- **Work with One File**:  
  Interact with a single file to view its data, write messages into its slack space, and clear its slack space.
- **System Checkup**:  
  Perform a system-wide cleanup of slack spaces.
- **Store File in Slack Space**:  
  Split an input file into smaller parts and store them in the slack spaces of newly created files.
- **Recover Stored File**:  
  Reconstruct a file previously stored in slack space by retrieving and combining its parts.

## Requirements

This project uses Python and manages dependencies with [Poetry](https://python-poetry.org/).

## Installation

Clone the repository:

    git clone https://github.com/gabriel-biudes-dev/slack-space-manager.git
   
    cd slack-space-manager

Install Poetry:

    pip install poetry

Install the dependencies:

    poetry install

Usage

Run the program with:

    sudo python3 main.py

**Main Menu**

Upon starting the program, the following main menu will appear:

    Option 1: Work with One File
    Opens a secondary menu for single-file operations:

    Choose an option:
        1) Show file data
        2) Write message on file slack space
        3) Clear file slack space

        Show File Data: View the content of the selected file.
        Write Message: Store a custom message in the slack space of the file.
        Clear Slack Space: Erase any data previously stored in the slack space.

    Option 2: System Checkup
    Clears slack spaces across the entire system and identifies potential file corruption issues. Use with caution and back up critical data beforehand.

    Option 3: Store File in Slack Space
    Splits a selected file into smaller parts and stores them in the slack spaces of newly created files. The program manages file splitting and storage based on the size of the original file.

    Option 4: Recover Stored File
    Retrieves and reconstructs a file previously stored in slack space by combining its parts from the associated files.

**How It Works**

Slack space refers to the unused portion of a disk cluster after a file is written. This tool takes advantage of this space for specialized operations:

    Perform targeted operations on a single file.
    Conduct system-wide maintenance of slack spaces.
    Utilize slack space for secure file storage and recovery.

**Limitations**

    No Command-Line Parameters: All interactions occur through the menu interface.
    Permissions: Administrative rights may be required for certain operations, especially system checkups.
