#!/usr/bin/env python3
"""
Create necessary directories for driaClaude
"""

import os
from pathlib import Path

# Directories to create
directories = [
    "data",
    "voices",
    "outputs",
    "static",
    "templates"
]

# Create directories
for dir_name in directories:
    Path(dir_name).mkdir(exist_ok=True)
    print(f"Created directory: {dir_name}")

print("\nAll directories created successfully!")