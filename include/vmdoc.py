"""
[vmdoc:description]
Automatically generate .md files using tags inside of files
[vmdoc:enddescription]
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))
sys.path.append(str(Path(__file__).resolve().parents[1]))
sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(str(Path(__file__).resolve().parents[4]))
sys.path.append(str(Path(__file__).resolve().parents[5]))

from vicmil_pip.packages.pyUtil import *
import hashlib
from typing import List, Optional, Tuple


def update_nav_section(mkdocs_yml_path: str, nav_section_name: str, section_entries: List[Tuple[str, str]]):
    """
    Updates the mkdocs.yml file by replacing or inserting a section under 'nav'.

    Args:
        mkdocs_yml_path: Path to the mkdocs.yml file.
        nav_section_name: The name of the section to update (e.g., 'files').
        section_entries: List of (source_filename, target_path) tuples.
                         Example: [('file1.py', 'vmdoc/file1_hash.txt'), ...]
    """
    pip_manager = PipManager()
    pip_manager.add_pip_package("PyYAML")
    pip_manager.install_missing_modules()

    import yaml
    if not os.path.exists(mkdocs_yml_path):
        print(f"mkdocs.yml not found at: {mkdocs_yml_path}")
        return

    with open(mkdocs_yml_path, 'r') as f:
        config = yaml.safe_load(f) or {}

    nav = config.get("nav", [])
    if not isinstance(nav, list):
        print("Invalid format: 'nav' section should be a list.")
        return

    # Remove any existing section with the given name
    nav = [item for item in nav if not (isinstance(item, dict) and nav_section_name in item)]

    # Convert tuples to dicts for YAML formatting
    nav_section_items = [{source: target} for source, target in section_entries]

    # Add the new section
    nav.append({nav_section_name: nav_section_items})
    config["nav"] = nav

    with open(mkdocs_yml_path, 'w') as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"Updated '{nav_section_name}' section in mkdocs.yml.")


class VmDocsGenerator:
    def __init__(self, docs_dir: str = None):
        self.pattern_matcher = GitignorePatternMatcher()
        
        self.pattern_matcher.add_pattern_str(
        """
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
        *venv/*
        *vmdoc/*
        node_modules/*
        build/*
        dist/*

        # Exclude specific log files
        *.log
        *.tmp
        """)

        self.files = set()

        self.docs_dir = docs_dir

        self._added_files = list()


    def set_pattern(self, gitignore_pattern: str):
        self.pattern_matcher = GitignorePatternMatcher()
        self.pattern_matcher.add_pattern_str(gitignore_pattern)


    def add_files_in_dir(self, dir_path: str):
        # List all matching files according to .gitignore-like rules
        files_full_path = self.pattern_matcher.list_matching_files(dir_path)
        for file_path in files_full_path:
            file_relative_path = file_path.replace(dir_path, "")
            self.files.add((file_path, file_relative_path))


    def _get_file_basename(self, src_relative_path):
        return str(os.path.basename(src_relative_path).replace("__", "_"))


    def _get_file_base_name_with_hash(self, src_relative_path):
        file_hash = hash_path(src_relative_path)
        base_name = self._get_file_basename(src_relative_path)
        return f"{base_name}_{file_hash}"


    def _update_mkdocs_yml_file(self):
        """
        Update the mkdocs.yml file to reflect the current list of documentation files.
        This method removes any existing `nav > files:` section and replaces it with
        entries pointing to generated markdown files under `docs/vmdoc/`.
        """
        mkdocs_yml_file_path = os.path.join(self.docs_dir, "mkdocs.yml")
        if not os.path.exists(mkdocs_yml_file_path):
            print(f"mkdocs.yml not found at {mkdocs_yml_file_path}")
            return

        with open(mkdocs_yml_file_path, 'r') as f:
            lines = f.readlines()

        lines = self._remove_old_nav_files_section(lines)
        new_entries = self._generate_nav_file_entries()
        if len(new_entries) > 0:
            lines = self._insert_new_nav_files_section(lines, new_entries)

        with open(mkdocs_yml_file_path, 'w') as f:
            f.writelines(lines)

        print("Updated mkdocs.yml successfully.")


    def _generate_nav_file_entries(self):
        """
        Generate a list of YAML-formatted strings representing the new 'files:' section
        entries for mkdocs.yml under the 'nav' section.
        """
        entries = []
        for _, rel_path in sorted(self._added_files):
            doc_name = self._get_file_base_name_with_hash(rel_path)
            md_file_path = f"vmdoc/{doc_name}.txt"
            entries.append(f"    - {rel_path}: {md_file_path}")
        return entries


    def _remove_old_nav_files_section(self, lines):
        """
        Removes the existing '- files:' section and all indented sub-entries from the `nav:` block.
        Returns the cleaned list of lines.
        """
        updated_lines = []
        in_nav = False
        in_files_section = False
        indent_level = None

        for line in lines:
            stripped = line.strip()

            if stripped == "nav:":
                in_nav = True
                updated_lines.append(line)
                continue

            if in_nav:
                if stripped.startswith("- files:"):
                    in_files_section = True
                    indent_level = len(line) - len(line.lstrip())
                    continue  # Skip this line and its children

                if in_files_section:
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent > indent_level:
                        continue  # Still inside old files section
                    else:
                        in_files_section = False  # End of old files section

            updated_lines.append(line)

        return updated_lines


    def _insert_new_nav_files_section(self, lines, new_entries):
        """
        Inserts the new `- files:` section into the `nav:` block of mkdocs.yml.
        Inserts after the 'nav:' key.
        """
        for i, line in enumerate(lines):
            if line.strip() == "nav:":
                insert_index = i + 1
                break
        else:
            insert_index = len(lines)

        insertion = ["  - files:\n"] + [f"{entry}\n" for entry in new_entries]
        return lines[:insert_index] + insertion + lines[insert_index:]


    def _update_vmdoc_file(self):
        vmdoc_md_file_path = f"{self.docs_dir}/docs/vmdoc/vmdocs.md"

        # List all the files with their description, and include a link to them
        # Prepare the vmdocs.md overview file
        vmdoc_description = "# Vmdoc Overview\n\nThis document lists all the generated documentation files.\n\n"

        for src_file_path, src_relative_path in self._added_files:
            description = get_docs_tag_contents_joined(src_file_path, '[vmdoc:description ]'.replace(" ", ""), '[vmdoc:enddescription ]'.replace(" ", ""))
            base_name_with_hash = self._get_file_base_name_with_hash(src_relative_path)

            vmdoc_description += f"- [{src_relative_path}]( {base_name_with_hash}.md ) - {description}\n\n"

        with open(vmdoc_md_file_path, 'w', encoding='utf-8') as f:
            f.write(vmdoc_description)
        
        print(f"vmdocs.md file generated at: {vmdoc_md_file_path}")


    def generate(self):
        self._added_files = []

        os.makedirs(self.docs_dir+"/docs/vmdoc", exist_ok=True)

        for src_file_path, src_relative_path in self.files:
            doc_tag_content = get_docs_tag_contents_joined(src_file_path, '[vmdoc:start ]'.replace(" ", ""), '[vmdoc:end ]'.replace(" ", ""))
            description_tag_content = get_docs_tag_contents_joined(src_file_path, '[vmdoc:description ]'.replace(" ", ""), '[vmdoc:enddescription ]'.replace(" ", ""))

            if len(doc_tag_content) == 0 and len(description_tag_content) == 0:
                # Do not add file without vmdoc tags
                continue

            self._added_files.append((src_file_path, src_relative_path)) # Mark that we have added the file to the documentation

            base_name_with_hash = self._get_file_base_name_with_hash(src_relative_path)
            md_file_name = base_name_with_hash + ".md"
            txt_file_name = base_name_with_hash + ".txt"

            output_md_path = f"{self.docs_dir}/docs/vmdoc/{md_file_name}" 
            output_txt_path = f"{self.docs_dir}/docs/vmdoc/{txt_file_name}" 

            metadata = (
            f"---\n"
            f"title: {src_relative_path}\n"
            f"source_file: {src_relative_path}\n"
            f"description: {description_tag_content}\n"
            f"generated_from: vmdoc\n"
            f"source_code_file: {txt_file_name}\n"
            f"---\n\n")

            body = (
                f"[📄 View raw source code]({txt_file_name})"
                f"\n\n"
                f"{doc_tag_content.strip()}\n\n"
            )

            with open(output_md_path, 'w', encoding='utf-8') as f:
                f.write(metadata + body)

            # Write raw source to .txt
            try:
                with open(src_file_path, 'r', encoding='utf-8') as src_file:
                    source_code = src_file.read()
                with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(source_code)
            except Exception as e:
                print(f"Error writing source code to txt: {e}")

        self._update_mkdocs_yml_file()
        self._update_vmdoc_file()



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


def get_docs_tag_contents_joined(file_path: str, start_tag: str, end_tag: str) -> str:
    doc_tag_content = get_docs_tag_contents(file_path, start_tag, end_tag)
    return ('\n\n'.join(doc_tag_content)).strip()

