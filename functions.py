import logging

from copy import deepcopy
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject


logger = logging.getLogger(__name__)


def get_page_read(
    tg_object: Message | CallbackQuery,
    storage: dict,
    user_books: dict,
    key: str
) -> tuple[int, int, str]:

    page_number = storage[str(tg_object.from_user.id)][storage['book']][key]
    last_number = len(user_books[storage['book']])
    page = user_books[storage['book']][page_number]
    return page_number, last_number, page


async def fill_storage(
    tg_obgect: Message | CallbackQuery,
    state: FSMContext,
    user_books: dict,
    user_dict_template: dict
) -> None:

    user_id = str(tg_obgect.from_user.id)
    user_db = {user_id: {}}
    for name_book in user_books:
        user_db[user_id][name_book] =\
            deepcopy(user_dict_template)

    await state.update_data(user_db, book=None)


def get_page(
        tg_object: Message | CallbackQuery,
        storage: dict,
        user_books: dict,
        step=0
) -> tuple[int, str] | tuple[False]:

    user_id = str(tg_object.from_user.id)
    page_number = storage[user_id][storage['book']]['page']
    last_number = len(user_books[storage['book']])
    if 0 < (page_number + step) <= last_number:
        page_number += step
        page = user_books[storage['book']][page_number]
        return page_number, last_number, page
    return None, None, None


def add_bookmark(
        callback: CallbackQuery,
        storage: dict,
        user_books: dict,
) -> str | None:

    number, _, page = get_page(callback, storage, user_books)
    bookmark = f'{number} {page[:30]}...'

    if bookmark not in storage[str(callback.from_user.id)][storage['book']]['bookmarks']:
        storage[str(callback.from_user.id)][storage['book']]['bookmarks'].append(
            bookmark)
        return bookmark


def get_user_bookmarks(
    storage: dict,
    tg_object: Message | CallbackQuery,
    _del=''
) -> list[str]:

    return sorted(map(lambda x: x + _del,
                      storage[str(tg_object.from_user.id)][storage['book']]['bookmarks']))


def move_to_bookmark(
    callback: CallbackQuery,
    storage: dict,
    user_books: dict,
) -> tuple[int, str]:

    number = int(callback.data.split()[0])
    last_number = len(user_books[storage['book']])
    storage[str(callback.from_user.id)][storage['book']]['page'] = number
    page = user_books[storage['book']][number]
    return number, last_number, page


def delete_bookmark(
    callback: CallbackQuery,
    storage: dict
) -> None | list:

    bookmark = callback.data
    name_book = storage['book']
    bookmarks = storage[str(callback.from_user.id)][name_book]['bookmarks']
    for i, bm in enumerate(bookmarks):
        if bm.split()[0] == bookmark.split()[0]:
            storage[str(callback.from_user.id)][name_book]['bookmarks'].pop(i)
            return sorted(
                storage[str(callback.from_user.id)][name_book]['bookmarks']
            )


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
