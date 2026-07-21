import re

MAX_PROMPT_LENGTH = 2000  # characters — tune later if needed

BLOCKED_PATTERNS = {
    "role_override": [
        r"ignore (all )?(previous|prior|above) instructions",
        r"disregard (your|the) (rules|guidelines|instructions)",
        r"you are now (DAN|no longer|free from)",
        r"forget (everything|what) (you were|i) told",
        r"act as (if you have|though you have) no restrictions",
        r"pretend (you are|to be) (an? )?(unfiltered|uncensored|unrestricted)",
        r"ignore all restrictions",
    ],
    "persona_jailbreaks": [
        r"\bDAN\b",
        r"developer mode",
        r"jailbreak(ed)?",
        r"opposite (day|mode)",
        r"evil (twin|confidant|version)",
    ],
    "system_prompt_extraction": [
        r"(reveal|show|print|repeat) (your|the) (system prompt|instructions)",
        r"what (are|were) you told (to do|before)",
        r"repeat (everything|the text) above",
    ],
    "privilege_escalation": [
        r"as an? (admin|administrator|root|developer) (user|account)?",
        r"i (am|'m) (your|the) (creator|developer|admin)",
        r"override safety (settings|protocols)",
    ],
}

ROLE_INJECTION_PATTERNS = [
    r"^\s*system\s*:",
    r"^\s*assistant\s*:",
    r"\[/?(system|assistant)\]",
    r"<\|(system|assistant)\|>",
]


def check_length(message: str) -> tuple[bool, str]:
    if len(message) > MAX_PROMPT_LENGTH:
        return False, f"Message exceeds max length of {MAX_PROMPT_LENGTH} characters"
    return True, ""


def check_blocked_patterns(message: str) -> tuple[bool, str]:
    for category, patterns in BLOCKED_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False, f"Blocked: matched {category} pattern"
    for pattern in ROLE_INJECTION_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return False, "Blocked: attempted role injection"
    return True, ""


def apply_firewall(message: str) -> tuple[bool, str]:
    """Returns (is_safe, reason_if_blocked)"""
    ok, reason = check_length(message)
    if not ok:
        return False, reason
    ok, reason = check_blocked_patterns(message)
    if not ok:
        return False, reason
    return True, ""