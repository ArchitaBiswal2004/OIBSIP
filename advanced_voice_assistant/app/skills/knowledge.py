import wikipedia

def get_knowledge(query):
    try:
        topic = query.replace("who is", "").replace("what is", "").strip()
        summary = wikipedia.summary(topic, sentences=2)
        return summary
    except:
        return "Sorry, I could not find information on that topic."
