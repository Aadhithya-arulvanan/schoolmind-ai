def detect_language(question):

    q = question.lower()

    languages = [
        "hindi",
        "tamil",
        "french",
        "german",
        "spanish",
        "telugu",
        "malayalam",
        "kannada"
    ]

    for language in languages:

        if language in q:

            return language.title()

    return None