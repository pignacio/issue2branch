from . import color

_PRIORITY_COLORS = {
    'immediate': color.bright_red,
    'urgent': color.red,
    'high': color.bright_yellow,
    'normal': color.bright_blue,
    'low': color.green,
}

_STATUS_COLORS = {
    'new': color.bright_yellow,
    'in progress': color.bright_cyan,
    'resolved': color.green,
    'closed': color.bright_green,
}

_TAG_COLORS = {
    'issue': color.magenta,
    'bug': color.bright_red,
    'enhancement': color.bright_blue,
    'documentation': color.yellow,
    'new feature': color.green,
    'feature': color.green,
}

def colorize(text, label=None):
    label = (label or text).lower()
    for color_dict in [_PRIORITY_COLORS, _STATUS_COLORS, _TAG_COLORS]:
        try:
            return color_dict[label](text)
        except KeyError:
            continue
    return text

