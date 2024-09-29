user_dict_template = {
    'page': 1,
    'last_page': 1,
    'bookmarks': set(),
    'continue': 1,
    'begin': 1
}

user_db: dict[int, dict[str, dict: user_dict_template]] = {}
