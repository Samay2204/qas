from .links import notes,pyq

# def processcommand(c):
            #     if "Previous Year Question" or "PYQ" in c.lower():
            #         if "Micro controller" in c.lower():
            #             link = links.web.get(micro controller)
            #             print("link")

def processCommand(c):

    if "note" in c or "notes" in c:
        for subject in notes: 
            if subject in c:
                return f"Here are the {subject.upper()} notes: {notes[subject]}"

    if "previous year question" in c or "pyq" in c:
        for subject in notes: 
            if subject in c:
                return f"Here are the {subject.upper()} PYQs: {pyq[subject]}"

    return None

