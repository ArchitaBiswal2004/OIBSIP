# app/core/state.py

_state = {
    "intent": None,
    "slots": {},
    "pending_slot": None
}

def start_intent(intent):
    _state["intent"] = intent
    _state["slots"] = {}
    _state["pending_slot"] = None

def require_slot(slot_name):
    _state["pending_slot"] = slot_name

def update_slot(slot_name, value):
    _state["slots"][slot_name] = value
    _state["pending_slot"] = None

def get_state():
    return _state

def clear_state():
    _state["intent"] = None
    _state["slots"] = {}
    _state["pending_slot"] = None
