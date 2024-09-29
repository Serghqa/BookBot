import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


logger = logging.getLogger(__name__)


def get_page_read(
        callback: CallbackQuery,
        user_db: dict,
        book: dict,
        name: str,
        key: str
) -> tuple[int, str]:
    number = user_db[callback.from_user.id][name][key]
    page = book[number]
    _update_user_bd(callback, user_db, name, number)
    return number, page


def _update_user_bd(
    callback: CallbackQuery,
    user_db: dict,
    name: str,
    number: int
) -> None:
    user_db[callback.from_user.id][name]['page'] = number
    if user_db[callback.from_user.id][name]['continue'] < number:
        user_db[callback.from_user.id][name]['continue'] = number


def get_page(
        callback: CallbackQuery,
        user_db: dict,
        book: dict,
        name: str,
        step=0
) -> tuple[int, str] | tuple[False]:
    number = user_db[callback.from_user.id][name]['page']
    if 0 < (number + step) <= len(book):
        number += step
        page = book[number]
        _update_user_bd(callback, user_db, name, number)
        return number, page
    return False, False


def add_bookmark(
        callback: CallbackQuery,
        user_db: dict,
        book: dict,
        name: str
) -> str:
    number, page = get_page(callback, user_db, book, name)
    bookmark = f'{number} {page[:30]}...'
    user_db[callback.from_user.id][name]['bookmarks'].add(
        f'{bookmark[:15]}...'
    )
    return bookmark


def get_user_bookmarks(
    tg_object: Message | CallbackQuery,
    user_db: dict,
    name: str,
    _del=''
) -> list[str]:
    return sorted(map(lambda x: x + _del,
                      user_db[tg_object.from_user.id][name]['bookmarks']))


def move_to_bookmark(
    callback: CallbackQuery,
    user_db: dict,
    book: dict,
    name: str
) -> tuple[int, str]:
    number = int(callback.data.split()[0])
    user_db[callback.from_user.id][name]['page'] = number
    page = book[number]
    return number, page


def delete_bookmark(
        callback: CallbackQuery,
        user_bd: dict,
        name: str
) -> None | list:
    bookmark = callback.data
    bookmarks = user_bd[callback.from_user.id][name]['bookmarks']
    for bm in bookmarks:
        if bm.split()[0] == bookmark.split()[0]:
            user_bd[callback.from_user.id][name]['bookmarks'].remove(bm)
            return sorted(user_bd[callback.from_user.id][name]['bookmarks'])


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]],
                Awaitable[Any]
                ],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data.get('event_from_user')
        if user:
            pass
        result = await handler(event, data)
        return result
