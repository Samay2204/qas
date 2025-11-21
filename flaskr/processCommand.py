from .links import notes, pyq, syllabus
from markupsafe import Markup

def make_link(url):
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'

def processCommand(c):
    c = c.lower()

    if "note" in c or "notes" in c:
        for subject in notes:
            if subject.lower() in c:
                link = make_link(notes[subject])
                return Markup(f"Here are the {subject.upper()} notes: {link}")

    if "previous year question" in c or "pyq" in c:
        for subject in pyq:
            if subject.lower() in c:
                link = make_link(pyq[subject])
                return Markup(f"Here are the {subject.upper()} PYQs: {link}")

    if "syllabus" in c:
        for subject in syllabus:
            if subject.lower() in c:
                link = make_link(syllabus[subject])
                return Markup(f"Here is the {subject.upper()} syllabus: {link}")

    return None
