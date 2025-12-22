"""Symbol definitions for 7-segment LED display.

Each symbol is defined as a list of blocks. Each block specifies:
- [0]: Segment number (1-7)
- [1]: Direction (0 = forward, 1 = backward)
- [2]: Start position (optional, default 0)
- [3]: End position (optional, default 14)

Display layout (7 segments per symbol position):
    ╔═══╗
    ║ 2 ║
    ╠═3═╣ <- segment 7 (middle)
    ║ 4 ║
    ╚═5═╝
    1   6
"""

from typing import List, Optional, Union

# Type aliases for clarity
BlockDef = List[int]  # [segment, direction] or [segment, direction, start, end]
SymbolDef = List[BlockDef]

# Colored block: (segment, direction, color_name) or (segment, direction, start, end, color_name)
ColoredBlockDef = tuple  # Tuple with color as last element
ColoredSymbolDef = List[ColoredBlockDef]

# Emoji to color name mapping
COLORS: dict[str, str] = {
    "❤️": "Красный",
    "🧡": "Оранжевый", 
    "💛": "Желтый",
    "💚": "Зеленый",
    "💙": "Синий",
    "💜": "Фиолетовый",
    "🖤": "Черный",
    "🤍": "Белый",
    "🤎": "Коричневый",
}

# Special action emojis
EMOJI_RAINBOW = "🌈"
EMOJI_TEMPERATURE = "🌡"
EMOJI_SLOTS = "🎰"

# Color name to RGB mapping
# Note: Values may be adjusted for specific LED hardware
RGB_COLORS: dict[str, tuple[int, int, int]] = {
    "Красный": (255, 0, 0),
    "Оранжевый": (255, 0, 135),
    "Желтый": (255, 0, 255),
    "Зеленый": (0, 0, 255),
    "Синий": (0, 255, 0),
    "Фиолетовый": (255, 165, 0),
    "Черный": (0, 0, 0),
    "Белый": (255, 255, 255),
    "Коричневый": (165, 42, 42),
}

# Numeric digit definitions (0-9)
NUMBERS: dict[int, SymbolDef] = {
    0: [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0]],
    1: [[1, 1], [6, 1]],
    2: [[2, 1], [1, 1], [7, 0], [4, 0], [5, 0]],
    3: [[2, 1], [1, 1], [7, 0], [6, 1], [5, 1]],
    4: [[3, 0], [7, 1], [1, 0], [6, 1]],
    5: [[2, 0], [3, 0], [7, 1], [6, 1], [5, 1]],
    6: [[2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]],
    7: [[2, 1], [1, 1], [6, 1]],
    8: [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]],
    9: [[7, 0], [3, 1], [2, 1], [1, 1], [6, 1], [5, 1]],
}

# Basic character definitions (Russian and English letters, simple symbols)
CHARS: dict[str, SymbolDef] = {
    # Russian letters
    "А": [[6, 0], [1, 0], [2, 0], [3, 0], [4, 0], [7, 1]],
    "Б": [[2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]],
    "В": [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]],
    "Г": [[2, 0], [3, 0], [4, 0]],
    "Е": [[2, 0], [3, 0], [4, 0], [5, 0], [7, 0]],
    "Ё": [[2, 0], [3, 0], [4, 0], [5, 0], [7, 0]],
    "З": [[2, 1], [1, 1], [6, 1], [5, 1], [7, 0]],
    "Н": [[3, 0], [4, 0], [7, 1], [1, 0], [6, 1]],
    "О": [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0]],
    "П": [[6, 0], [1, 0], [2, 0], [3, 0], [4, 0]],
    "Р": [[7, 1], [1, 0], [2, 0], [3, 0], [4, 0]],
    "С": [[2, 0], [3, 0], [4, 0], [5, 0]],
    "Ь": [[3, 0], [4, 0], [5, 0], [6, 0], [7, 0]],
    "У": [[3, 0], [7, 1], [1, 1], [6, 1], [5, 1]],
    "Ч": [[3, 0], [7, 1], [1, 1], [6, 1]],
    
    # English letters
    "A": [[6, 0], [1, 0], [2, 0], [3, 0], [4, 0], [7, 1]],
    "B": [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0]],
    "C": [[2, 0], [3, 0], [4, 0], [5, 0]],
    "E": [[2, 0], [3, 0], [4, 0], [5, 0], [7, 0]],
    "H": [[3, 0], [4, 0], [7, 1], [1, 0], [6, 1]],
    "I": [[1, 1], [6, 1]],
    "J": [[1, 1], [6, 1], [5, 1]],
    "L": [[3, 0], [4, 0], [5, 1]],
    "O": [[1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0]],
    "P": [[7, 1], [1, 0], [2, 0], [3, 0], [4, 0]],
    "S": [[2, 0], [3, 0], [7, 1], [6, 1], [5, 1]],
    "U": [[3, 0], [4, 0], [5, 0], [6, 0], [1, 0]],
    "Y": [[3, 0], [7, 1], [1, 1], [6, 1], [5, 1]],
    
    # Basic symbols
    "-": [[7, 1]],
    " ": [],
    "_": [[5, 0]],
    "*": [[1, 0], [2, 0], [3, 0], [7, 1]],  # Degree symbol for temperature
}

# Special characters with custom segment ranges
SPECIAL_CHARS: dict[str, SymbolDef] = {
    # Russian letters requiring partial segments
    "Д": [[7, 1], [2, 0, 7, 8], [4, 0, 0, 3], [6, 0, 11, 14]],
    "Ж": [[3, 0, 0, 3], [4, 0, 11, 14], [5, 0, 7, 8], [7, 1, 7, 8], [2, 0, 7, 8], [1, 1, 11, 14], [6, 1, 0, 3]],
    "И": [[3, 0], [4, 0], [7, 1, 6, 9], [1, 1], [6, 1]],
    "Й": [[3, 0], [4, 0], [7, 1, 6, 9], [2, 1, 6, 9], [1, 1], [6, 1]],
    "К": [[3, 0], [4, 0], [7, 1, 11, 14], [1, 0, 11, 14], [5, 0, 11, 14]],
    "Л": [[4, 0, 11, 14], [7, 1, 3, 4], [2, 0, 7, 8], [7, 1, 11, 12], [6, 0, 0, 3]],
    "М": [[4, 1], [3, 1], [7, 1, 3, 4], [5, 0, 7, 8], [7, 1, 11, 12], [1, 1], [6, 1]],
    "Т": [[2, 1], [7, 1, 7, 8], [5, 1, 7, 8]],
    "Ф": [[7, 1, 7, 8], [7, 1, 0, 3], [1, 0], [2, 0, 0, 3], [2, 0, 7, 8], [2, 0, 11, 14], [3, 0], [7, 1, 11, 14], [5, 1, 7, 8]],
    "Х": [[3, 0, 0, 3], [4, 0, 11, 14], [7, 1, 7, 8], [1, 1, 11, 14], [6, 1, 0, 3]],
    "Ц": [[3, 0], [7, 1], [1, 1], [6, 1, 11, 14]],
    "Ш": [[3, 0], [4, 0], [5, 0, 7, 8], [7, 1, 7, 8], [2, 1, 7, 8], [1, 1], [6, 1]],
    "Щ": [[3, 0], [7, 1], [2, 1, 7, 8], [1, 1], [6, 1, 11, 14]],
    "Ъ": [[2, 1, 11, 14], [7, 1, 0, 10], [6, 1], [5, 1]],
    "Ы": [[3, 0], [4, 0], [7, 1, 8, 14], [5, 0, 0, 7], [6, 0], [1, 0]],
    "Э": [[2, 1, 2, 14], [1, 1, 0, 12], [6, 1, 2, 14], [5, 1, 0, 12], [7, 0, 0, 6]],
    "Ю": [[2, 0, 6, 9], [3, 0], [4, 0], [7, 1, 11, 14], [5, 0, 6, 9], [6, 0, 6, 9], [1, 0, 6, 9]],
    "Я": [[5, 0, 0, 3], [6, 0], [1, 0], [2, 0], [3, 0], [7, 1]],
    
    # English letters requiring partial segments
    "D": [[3, 0], [4, 0], [2, 1, 3, 14], [1, 1, 0, 11], [6, 1, 3, 14], [5, 1, 0, 11]],
    "F": [[2, 0], [3, 0], [4, 0], [7, 1, 6, 14]],
    "G": [[2, 0], [3, 0], [4, 0], [5, 0], [6, 0, 0, 6]],
    "K": [[3, 0], [4, 0], [7, 1, 11, 14], [1, 0, 11, 14], [5, 0, 11, 14]],
    "M": [[4, 1], [3, 1], [7, 1, 3, 4], [5, 0, 7, 8], [7, 1, 11, 12], [1, 1], [6, 1]],
    "N": [[3, 1], [4, 1], [7, 1, 6, 9], [6, 0], [1, 0]],
    "Q": [[6, 0], [1, 0], [2, 0], [3, 0], [7, 1]],
    "R": [[4, 1], [3, 1], [2, 1, 0, 7], [1, 1, 6, 9], [7, 0, 8, 14], [6, 1, 12, 14]],
    "T": [[2, 1], [7, 1, 7, 8], [5, 1, 7, 8]],
    "V": [[3, 0, 0, 3], [7, 1, 3, 4], [5, 0, 7, 8], [7, 1, 11, 12], [1, 0, 11, 14]],
    "W": [[3, 0, 0, 3], [7, 1, 2, 3], [5, 0, 4, 5], [7, 1, 7, 8], [5, 0, 10, 11], [7, 1, 11, 12], [1, 0, 11, 14]],
    "X": [[3, 0, 0, 3], [4, 0, 11, 14], [7, 1, 7, 8], [1, 1, 11, 14], [6, 1, 0, 3]],
    "Z": [[2, 1], [7, 0, 6, 9], [5, 0]],
    
    # Punctuation
    ".": [[5, 0, 6, 9]],
    ",": [[4, 0, 11, 13]],
    "'": [[3, 0, 0, 2]],
    "!": [[3, 0], [4, 0, 0, 7], [4, 0, 13, 14]],
    ":": [[3, 0, 7, 8], [4, 0, 7, 8]],
    ";": [[3, 0, 7, 8], [4, 0, 11, 13]],
    "[": [[2, 0, 9, 14], [3, 0], [4, 0], [5, 0, 0, 5]],
    "]": [[2, 1, 0, 5], [1, 1], [6, 1], [5, 1, 9, 14]],
    "?": [[2, 1], [1, 1], [7, 0], [4, 1, 0, 7], [4, 1, 13, 14]],
}

# Slot machine symbols with colors
# Each block is (segment, direction, color_name) or (segment, direction, start, end, color_name)
# Order matters for animation sequence!
SLOT_SYMBOLS: dict[str, ColoredSymbolDef] = {
    # Seven (7) - Red color, styled like casino 7 with middle line
    # Sequence: segment 2 backward, segment 1 backward, segment 7 forward, segment 4 forward
    "seven": [
        (2, 1, "Красный"),
        (1, 1, "Красный"),
        (7, 0, "Красный"),
        (4, 0, "Красный"),
    ],
    
    # BAR - White color, letter B shape
    # Using standard B definition: all segments lit
    "bar": [
        (1, 0, "Белый"),
        (2, 0, "Белый"),
        (3, 0, "Белый"),
        (4, 0, "Белый"),
        (5, 0, "Белый"),
        (6, 0, "Белый"),
        (7, 0, "Белый"),
    ],
    
    # Lemon - Yellow body with green stem
    # Yellow: segments 7, 4, 5, 6 (forward) - the fruit body
    # Green: segments 1, 2 (forward) - the stem/leaf
    "lemon": [
        (7, 0, "Желтый"),
        (4, 0, "Желтый"),
        (5, 0, "Желтый"),
        (6, 0, "Желтый"),
        (1, 0, "Зеленый"),
        (2, 0, "Зеленый"),
    ],
    
    # Grapes - Purple berries with brown stem and green leaf
    # Purple: segments 7, 4, 5, 6 (forward) - the grape cluster
    # Brown: segment 1 (forward) - the stem
    # Green: segment 2 (forward) - the leaf
    "grapes": [
        (7, 0, "Фиолетовый"),
        (4, 0, "Фиолетовый"),
        (5, 0, "Фиолетовый"),
        (6, 0, "Фиолетовый"),
        (1, 0, "Коричневый"),
        (2, 0, "Зеленый"),
    ],
}


def get_symbol_definition(symbol: Union[str, int]) -> Optional[SymbolDef]:
    """Get the block definition for a symbol.
    
    Args:
        symbol: Character or digit to look up
        
    Returns:
        List of block definitions or None if symbol not found
    """
    if isinstance(symbol, int):
        return NUMBERS.get(symbol)
    
    if symbol in CHARS:
        return CHARS[symbol]
    
    if symbol in SPECIAL_CHARS:
        return SPECIAL_CHARS[symbol]
    
    return None


def get_slot_symbol_definition(slot_name: str) -> Optional[ColoredSymbolDef]:
    """Get the colored block definition for a slot machine symbol.
    
    Args:
        slot_name: One of 'bar', 'grapes', 'lemon', 'seven'
        
    Returns:
        List of colored block definitions or None if symbol not found
    """
    return SLOT_SYMBOLS.get(slot_name)


def get_slot_combo_parts(dice_value: int) -> List[str]:
    """Get slot machine symbols from dice value.
    
    Converts dice value (1-64) to list of three slot symbols.
    Order is left to right (first displayed to last displayed).
    
    Args:
        dice_value: Dice value from Telegram (1-64)
        
    Returns:
        List of 3 slot symbol names: ['bar'/'grapes'/'lemon'/'seven', ...]
    """
    #           0       1         2        3
    values = ["bar", "grapes", "lemon", "seven"]
    
    dice_value -= 1
    result = []
    for _ in range(3):
        result.append(values[dice_value % 4])
        dice_value //= 4
    return result


def is_slot_jackpot(dice_value: int) -> bool:
    """Check if dice value is a winning combination (three of a kind).
    
    Args:
        dice_value: Dice value from Telegram (1-64)
        
    Returns:
        True if all three slots match
    """
    # Three-of-a-kind values: 1 (bar-bar-bar), 22 (grapes-grapes-grapes), 
    # 43 (lemon-lemon-lemon), 64 (seven-seven-seven)
    return dice_value in (1, 22, 43, 64)


def is_displayable(text: str) -> bool:
    """Check if all characters in text can be displayed.
    
    Args:
        text: String to check
        
    Returns:
        True if all characters are displayable
    """
    for char in text:
        if char.isdigit():
            continue
        if char not in CHARS and char not in SPECIAL_CHARS:
            return False
    return True
