import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from numpy import random


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def check_lookup_spelling(lookup):
    entries = list_entries()
    potential_entries = []
    for entry in entries:
        check = re.search(lookup, entry, re.IGNORECASE)
        if check:
            potential_entries.append(entry)
    
    return potential_entries

def validate_title(title):
    entries = list_entries()
    title = title.casefold()
    for entry in entries:
        entry = entry.casefold()
        if title == entry:
            return False
    
    return True

def find_random_entry():
    entryList = list_entries()
    # listCount = len(entryList)
    return entryList[random.randint(len(entryList))]
