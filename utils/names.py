NAMES = [
    "SteveBot",
    "AlexBot",
    "BertBot"
]


def get_agent_names(n):
    return [get_name(i) for i in range(n)]


def get_name(i):
    return NAMES[i] if i < len(NAMES) else f"Bot {i}"
