import os


MARKS = '.,:;&!'
PAGE_SIZE = 500


books: dict[str, dict] = {}


def prepare_book(path: str, book: dict) -> dict[int, str]:
    page = 1
    start = 0
    with open(path, encoding='utf8') as f:
        text = f.read()
        fragment, size = _get_part_text(text, start, PAGE_SIZE)
        while fragment and size:
            book[page] = fragment
            page += 1
            start = start + size
            fragment, size = _get_part_text(text, start, PAGE_SIZE)
    return book


def _get_part_text(text: str, start: int, page_size: int) -> tuple[str, int]:
    text_size = len(text)
    if (start + page_size) >= text_size:
        return text[start:], len(text[start:])
    fragment = text[start:start+page_size]
    if fragment[-1] in MARKS and text[start+page_size] not in MARKS:
        return fragment, page_size
    return _get_part_text(text, start, page_size+1)


PATH_FOLDER = 'books'
for path_file in os.listdir(PATH_FOLDER):
    name_book = os.path.splitext(path_file)[0]
    books[name_book] = prepare_book(os.path.join(PATH_FOLDER, path_file), {})
