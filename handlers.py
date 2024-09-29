import logging

from copy import deepcopy

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery

from keyboards import (
    create_keyboard,
    create_keyboard_bookmarks,
    create_keyboard_del_bookmarks,
)
from database import user_db, user_dict_template
from file_handling import books as user_books
from functions import (
    get_page,
    add_bookmark,
    get_user_bookmarks,
    delete_bookmark,
    get_page_read,
    move_to_bookmark
)
from filters import IsBookmarks, MoveToBookmark, DelBookmark
from lexicon import HANDLERS_LEXICON, KEYBOARDS_LEXICON


logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):

    if message.from_user.id not in user_db:
        user_db[message.from_user.id] = {}
        for name_book, book in user_books.items():
            user_db[message.from_user.id][name_book] =\
                deepcopy(user_dict_template)
            user_db[message.from_user.id][name_book]['last_page'] = len(book)

    await message.answer(
        text=HANDLERS_LEXICON[message.text],
        reply_markup=create_keyboard(
            *user_books,
            width=1
        )
    )


@router.message(F.text == '/help')
async def procces_help_command(message: Message):
    await message.answer(
        text='help'
    )


@router.message(F.text == '/beginning')
async def process_beginning_command(message: Message):

    if user_db:
        await message.answer(
            text=HANDLERS_LEXICON[message.text],
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON[message.text]
            )
        )

    else:
        await message.answer(
            text='Выбери книгу',
            reply_markup=create_keyboard(
                *user_books,
                width=1
            )
        )


@router.message(F.text == '/continue')
async def process_continue_command(message: Message):

    if user_db:
        await message.answer(
            text=HANDLERS_LEXICON[message.text],
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON[message.text]
            )
        )

    else:
        await message.answer(
            text='Выбери книгу',
            reply_markup=create_keyboard(
                *user_books,
                width=1
            )
        )


@router.message(F.text == '/bookmarks')
async def process_bookmarks_command(message: Message, state: FSMContext):

    if user_db:
        storage = await state.get_data()
        bookmakrs = get_user_bookmarks(message, user_db, storage['book'])
        if not bookmakrs:
            await message.answer(
                text='У вас нет закладок'
            )
        else:
            await message.answer(
                text=HANDLERS_LEXICON[message.text],
                reply_markup=create_keyboard_bookmarks(
                    *bookmakrs
                )
            )

    else:
        await message.answer(
            text='Выбери книгу',
            reply_markup=create_keyboard(
                *user_books,
                width=1
            )
        )


@router.message(F.text == '/books')
async def process_get_books(message: Message):

    await message.answer(
        text=HANDLERS_LEXICON[message.text],
        reply_markup=create_keyboard(
            *user_books,
            width=1
        )
    )


@router.callback_query(F.data.in_(user_books))
async def process_start_read_book(callback: CallbackQuery, state: FSMContext):

    name_book = callback.data
    await state.update_data(book=name_book)
    await callback.message.edit_text(
        text=f'Вы будете читать книгу {name_book}',
        reply_markup=create_keyboard(
            'Читать'
        )
    )


@router.callback_query(F.data == 'Читать')
async def process_start_read(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, page = get_page(
        callback,
        user_db,
        user_books[storage['book']],
        storage['book']
    )

    await callback.message.edit_text(
        text=page,
        reply_markup=create_keyboard(
            KEYBOARDS_LEXICON['prev'],
            f'{number}/'
            f'{user_db[callback.from_user.id][storage['book']]['last_page']}',
            KEYBOARDS_LEXICON['next']
        )
    )


@router.callback_query(F.data == '<<')
async def process_prev_page_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, page = get_page(
        callback,
        user_db,
        user_books[storage['book']],
        storage['book'],
        step=-1
    )

    if number and page:
        await callback.message.edit_text(
            text=page,
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON['prev'],
                f'{number}/{user_db[callback.from_user.id][storage['book']]['last_page']}',
                KEYBOARDS_LEXICON['next']
            )
        )

    else:
        await callback.answer()


@router.callback_query(F.data == '>>')
async def process_next_page_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, page = get_page(callback, user_db, user_books[storage['book']], storage['book'], step=1)

    if number and page:
        await callback.message.edit_text(
            text=page,
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON['prev'],
                f'{number}/{user_db[callback.from_user.id][storage['book']]['last_page']}',
                KEYBOARDS_LEXICON['next']
            )
        )

    else:
        await callback.answer()


@router.callback_query(F.data == 'Продолжить читать')
async def process_continue_read_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, page = get_page_read(callback, user_db, user_books[storage['book']], storage['book'], 'continue')

    await callback.message.edit_text(
        text=page,
        reply_markup=create_keyboard(
            KEYBOARDS_LEXICON['prev'],
            f'{number}/{user_db[callback.from_user.id][storage['book']]['last_page']}',
            KEYBOARDS_LEXICON['next']
        )
    )


@router.callback_query(F.data == 'В начало книги')
async def process_beggin_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, page = get_page_read(callback, user_db, user_books[storage['book']], storage['book'], 'begin')

    await callback.message.edit_text(
        text=page,
        reply_markup=create_keyboard(
            KEYBOARDS_LEXICON['prev'],
            f'{number}/{user_db[callback.from_user.id][storage['book']]['last_page']}',
            KEYBOARDS_LEXICON['next']
        )
    )


@router.callback_query(F.data == 'edit_bookmarks')
async def process_edit_bookmarks_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    bookmarks = get_user_bookmarks(
        callback,
        user_db,
        storage['book'],
        ' del'
    )

    await callback.message.edit_text(
        text='Удалить закладку',
        reply_markup=create_keyboard_del_bookmarks(*bookmarks)
    )


@router.callback_query(F.data == 'cancel')
async def process_cancel_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, page = get_page(callback, user_db, user_books[storage['book']], storage['book'])

    await callback.message.edit_text(
        text=page,
        reply_markup=create_keyboard(
            KEYBOARDS_LEXICON['prev'],
            f'{number}/{user_db[callback.from_user.id][storage['book']]['last_page']}',
            KEYBOARDS_LEXICON['next']
        )
    )


@router.callback_query(DelBookmark())
async def process_del_bookmark_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    bookmarks = delete_bookmark(callback, user_db, storage['book'])

    if not bookmarks:
        await callback.message.edit_text(
            text='У вас нет закладок',
            reply_markup=create_keyboard('Продолжить читать')
        )

    else:
        await callback.message.edit_text(
            text='Удалить закладку',
            reply_markup=create_keyboard_bookmarks(*bookmarks)
        )


@router.callback_query(IsBookmarks())
async def process_set_bookmark_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    bookmark = add_bookmark(callback, user_db, user_books[storage['book']], storage['book'])

    await callback.answer(text=f'Закладка {bookmark.split()[0]} добавлена')


@router.callback_query(MoveToBookmark())
async def process_move_to_bookmark(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, page = move_to_bookmark(callback, user_db, user_books[storage['book']], storage['book'])

    await callback.message.edit_text(
        text=page,
        reply_markup=create_keyboard(
            KEYBOARDS_LEXICON['prev'],
            f'{number}/{user_db[callback.from_user.id][storage['book']]['last_page']}',
            KEYBOARDS_LEXICON['next']
        )
    )


@router.message()
async def send_echo(message: Message):

    await message.answer(text=message.text)
    print(message.model_dump_json(indent=4))


@router.callback_query()
async def callback_answer(callback: CallbackQuery):

    await callback.answer()
    print(callback.model_dump_json(indent=4))
