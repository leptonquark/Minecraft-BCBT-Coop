NAMES = [
    "SteveBot",
    "AlexBot",
    "BertBot"
]


def get_agent_names(n):
    return [get_name(i) for i in range(n)]


def get_name(i):
    if i < len(NAMES):
        return NAMES[i]
    else:
        return f"Bot {i}"
