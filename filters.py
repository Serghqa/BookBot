from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery


class IsBookmarks(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        is_bookmark = callback.data.split('/')
        return len(is_bookmark) == 2 and \
            all(map(lambda x: x.isdigit(), is_bookmark))


class MoveToBookmark(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        bookmark = callback.data.split()
        return bookmark[0].isdigit()


class DelBookmark(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        bookmark = callback.data.split()
        return bookmark[0].isdigit() and bookmark[-1] == 'del'
