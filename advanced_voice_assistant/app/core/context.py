context = {
    "last_intent": None,
    "last_query": None
}

def update_context(intent, query):
    context["last_intent"] = intent
    context["last_query"] = query

def get_context():
    return context
