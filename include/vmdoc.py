"""
[vmdoc:description]
Automatically generate .md files using tags inside of files
[vmdoc:enddescription]
"""

import os
import fnmatch
import hashlib
from typing import List, Optional
import pathlib


def get_directory_path(__file__in, up_directories=0):
    return str(pathlib.Path(__file__in).parents[up_directories].resolve()).replace("\\", "/")


def get_docs_tag_contents(file_path: str, start_tag: str, end_tag: str) -> List[str]:
    """Extract content between the specified start and end tags from a file."""
    contents = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()

        start_positions = []
        end_positions = []

        start_pos = file_content.find(start_tag)
        while start_pos != -1:
            start_positions.append(start_pos)
            start_pos = file_content.find(start_tag, start_pos + len(start_tag))

        end_pos = file_content.find(end_tag)
        while end_pos != -1:
            end_positions.append(end_pos)
            end_pos = file_content.find(end_tag, end_pos + len(end_tag))

        if len(start_positions) != len(end_positions):
            print(f"Warning: Mismatched number of start and end tags in {file_path}")
            return contents

        for start, end in zip(start_positions, end_positions):
            if end > start:
                content = file_content[start + len(start_tag):end].strip()
                contents.append(content)

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    
    return contents


def hash_path(rel_path: str) -> str:
    """Generate a short hash of the relative path."""
    return hashlib.md5(rel_path.encode('utf-8')).hexdigest()[:6]


def parse_gitignore_string(gitignore_content: str):
    """Parse .gitignore-like content from a string into a list of (pattern, is_negation)."""
    pattern_list = []

    for line in gitignore_content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        is_negation = line.startswith('!')
        pattern = line[1:] if is_negation else line
        pattern_list.append((pattern, is_negation))

    return pattern_list


def match_gitignore_patterns(file_path: str, pattern_list: List[tuple]) -> bool:
    """Determine if a file should be included based on gitignore-like rules."""
    match = False  # Default: do not include

    for pattern, is_negation in pattern_list:
        if fnmatch.fnmatch(file_path, pattern):
            match = is_negation  # Override based on whether it's a negation (!)
    
    return match


def list_matching_files(directory_path: str, pattern_list: List[tuple]):
    """Return files matching the gitignore-like pattern list."""
    matching_files = []

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), directory_path).replace("\\", "/")
            if match_gitignore_patterns(rel_path, pattern_list):
                matching_files.append(os.path.join(root, file))

    return matching_files


def generate_markdown_file(src_rel_path: str, src_abs_path: str, output_dir: str, description: str, doc_tag_content: str) -> None:
    """Generate a markdown file with extracted content and link to raw source as .txt."""
    file_hash = hash_path(src_rel_path)
    base_name = os.path.basename(src_rel_path)
    md_file_name = f"{base_name}_{file_hash}.md"
    txt_file_name = f"{base_name}_{file_hash}.txt"

    output_md_path = os.path.join(output_dir, md_file_name)
    output_txt_path = os.path.join(output_dir, txt_file_name)

    metadata = (
        f"---\n"
        f"title: {src_rel_path}\n"
        f"source_file: {src_rel_path}\n"
        f"description: {description}\n"
        f"generated_from: vmdoc\n"
        f"source_code_file: {txt_file_name}\n"
        f"---\n\n"
    )

    body = (
        f"[📄 View raw source code]({txt_file_name})"
        f"\n\n"
        f"{doc_tag_content.strip()}\n\n"
        
        
    )

    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(metadata + body)

    # Write raw source to .txt
    try:
        with open(src_abs_path, 'r', encoding='utf-8') as src_file:
            source_code = src_file.read()
        with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(source_code)
    except Exception as e:
        print(f"Error writing source code to txt: {e}")


def vmdoc_generate_markdown_files(
    src_dir: str,
    output_dir: str,
    gitignore_content: Optional[str] = None
) -> None:
    """Generate markdown files from source files, with gitignore-like pattern support."""
    # Default .gitignore content if not provided
    if gitignore_content is None:
        gitignore_content = """
        # Exclude everything by default
        *

        # Include code files
        !*.py
        !*.cpp
        !*.h
        !*.hpp
        !*.java
        !*.js

        # Exclude directories
        venv/*
        node_modules/*
        build/*
        dist/*

        # Exclude specific log files
        *.log
        *.tmp
        """
    
    # Parse the .gitignore-like string content
    pattern_list = parse_gitignore_string(gitignore_content)
    
    # List all matching files according to .gitignore-like rules
    files = list_matching_files(src_dir, pattern_list)
    print("matched files:", files)

    # Prepare the vmdocs.md overview file
    vmdoc_description = "# Vmdoc Overview\n\nThis document lists all the generated documentation files.\n\n"

    for file_path in files:
        doc_tag_content = get_docs_tag_contents(file_path, '[vmdoc:start ]'.replace(" ", ""), '[vmdoc:end ]'.replace(" ", ""))
        description_tag_content = get_docs_tag_contents(file_path, '[vmdoc:description]', '[vmdoc:enddescription]')
        if len(doc_tag_content) == 0 and len(description_tag_content) == 0:
            continue

        description = description_tag_content[0] if description_tag_content else "No description provided."

        relative_path = os.path.relpath(file_path, src_dir)
        generate_markdown_file(relative_path, file_path, output_dir, description, '\n\n'.join(doc_tag_content))

        vmdoc_description += f"- [{relative_path.replace(os.sep, '/')}]( {os.path.basename(relative_path)}_{hash_path(relative_path)}.md ) - {description}\n"

    with open(os.path.join(output_dir, 'vmdocs.md'), 'w', encoding='utf-8') as f:
        f.write(vmdoc_description)
    
    print(f"vmdocs.md file generated at: {os.path.join(output_dir, 'vmdocs.md')}")


if __name__ == "__main__":
    print(get_docs_tag_contents(__file__, "[vmdoc:description]", "[vmdoc:enddescription]"))
    src_dir = get_directory_path(__file__)
    output_dir = os.path.join(src_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    vmdoc_generate_markdown_files(src_dir, output_dir)
