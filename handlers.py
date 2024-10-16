import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from keyboards import (
    create_keyboard,
    create_keyboard_bookmarks,
    create_keyboard_del_bookmarks,
)
from database import user_dict_template
from file_handling import books as user_books
from functions import (
    get_page,
    add_bookmark,
    get_user_bookmarks,
    delete_bookmark,
    get_page_read,
    move_to_bookmark,
    fill_storage
)
from filters import IsBookmarks, MoveToBookmark, DelBookmark
from lexicon import HANDLERS_LEXICON, KEYBOARDS_LEXICON


logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    #  await state.clear()
    storage = await state.get_data()
    if str(message.from_user.id) not in storage:
        await fill_storage(
            message,
            state,
            user_books,
            user_dict_template
        )

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
async def process_beginning_command(message: Message, state: FSMContext):

    storage = await state.get_data()
    if storage['book']:
        if storage[str(message.from_user.id)][storage['book']]['page'] != 1:
            await message.answer(
                text=HANDLERS_LEXICON['beginning']
            )

        number, last_number, page = get_page_read(
            message,
            storage,
            user_books,
            'begin'
        )
        storage[str(message.from_user.id)][storage['book']]['page'] = number
        await state.update_data(storage)

        await message.answer(
            text=page,
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON['prev'],
                f'{number}/{last_number}',
                KEYBOARDS_LEXICON['next']
            )
        )
    else:
        await message.answer(
            text=HANDLERS_LEXICON['book_selection'],
            reply_markup=create_keyboard(
                *user_books,
                width=1
            )
        )


@router.message(F.text == '/continue')
async def process_continue_command(message: Message, state: FSMContext):

    storage = await state.get_data()
    if storage['book']:
        await message.answer(
            text=HANDLERS_LEXICON[message.text]
        )

        number, last_number, page = get_page_read(
            message,
            storage,
            user_books,
            'continue'
        )
        storage[str(message.from_user.id)][storage['book']]['page'] = number
        await state.update_data(storage)

        await message.answer(
            text=page,
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON['prev'],
                f'{number}/{last_number}',
                KEYBOARDS_LEXICON['next']
            )
        )

    else:
        await message.answer(
            text=HANDLERS_LEXICON['book_selection'],
            reply_markup=create_keyboard(
                *user_books,
                width=1
            )
        )


@router.message(F.text == '/bookmarks')
async def process_bookmarks_command(message: Message, state: FSMContext):

    storage = await state.get_data()
    if storage['book']:
        bookmarks = get_user_bookmarks(
            storage,
            message
        )
        if not bookmarks:
            await message.answer(
                text=HANDLERS_LEXICON['not_bookmarks']
            )
            number, last_number, page = get_page(
                message,
                storage,
                user_books
            )

            await message.answer(
                text=page,
                reply_markup=create_keyboard(
                    KEYBOARDS_LEXICON['prev'],
                    f'{number}/{last_number}',
                    KEYBOARDS_LEXICON['next']
                )
            )
        else:
            await message.answer(
                text=HANDLERS_LEXICON[message.text],
                reply_markup=create_keyboard_bookmarks(
                    *bookmarks
                )
            )

    else:
        await message.answer(
            text=HANDLERS_LEXICON['book_selection'],
            reply_markup=create_keyboard(
                *user_books,
                width=1
            )
        )


@router.message(F.text == '/books')
async def process_book_selection(message: Message):

    await message.answer(
        text=HANDLERS_LEXICON[message.text],
        reply_markup=create_keyboard(
            *user_books,
            width=1
        )
    )


@router.callback_query(F.data.in_(user_books))
async def process_book_start(callback: CallbackQuery, state: FSMContext):

    await state.update_data(book=callback.data)
    storage = await state.get_data()
    number, last_number, page = get_page(
        callback,
        storage,
        user_books
    )
    await callback.message.edit_text(
        text=page,
        reply_markup=create_keyboard(
            KEYBOARDS_LEXICON['prev'],
            f'{number}/{last_number}',
            KEYBOARDS_LEXICON['next']
        )
    )


@router.callback_query(F.data == '<<')
async def prev_page_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, last_number, page = get_page(
        callback,
        storage,
        user_books,
        step=-1
    )

    if number and page:
        await callback.message.edit_text(
            text=page,
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON['prev'],
                f'{number}/{last_number}',
                KEYBOARDS_LEXICON['next']
            )
        )
        storage[str(callback.from_user.id)][storage['book']]['page'] = number
        await state.update_data(storage)

    else:
        await callback.answer()


@router.callback_query(F.data == '>>')
async def next_page_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, last_number, page = get_page(
        callback,
        storage,
        user_books,
        step=1
    )

    if number and page:
        await callback.message.edit_text(
            text=page,
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON['prev'],
                f'{number}/{last_number}',
                KEYBOARDS_LEXICON['next']
            )
        )
        storage[str(callback.from_user.id)][storage['book']]['page'] = number
        storage[str(callback.from_user.id)][storage['book']]['continue'] = number
        await state.update_data(storage)

    else:
        await callback.answer()


@router.callback_query(F.data == 'edit_bookmarks')
async def edit_bookmarks_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    bookmarks = get_user_bookmarks(
        storage,
        callback,
        ' del'
    )

    await callback.message.edit_text(
        text=HANDLERS_LEXICON['delete_bookmark'],
        reply_markup=create_keyboard_del_bookmarks(
            *bookmarks
        )
    )


@router.callback_query(F.data == 'cancel')
async def cancel_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, last_number, page = get_page(
        callback,
        storage,
        user_books,
    )

    await callback.message.edit_text(
        text=page,
        reply_markup=create_keyboard(
            KEYBOARDS_LEXICON['prev'],
            f'{number}/{last_number}',
            KEYBOARDS_LEXICON['next']
        )
    )


@router.callback_query(DelBookmark())
async def del_bookmark(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    bookmarks = delete_bookmark(
        callback,
        storage
    )
    await state.update_data(storage)

    if not bookmarks:
        await callback.message.delete()
        await callback.answer(
            text=HANDLERS_LEXICON['not_bookmarks']
        )
        number, last_number, page = get_page(
            callback,
            storage,
            user_books,
        )
        await callback.message.answer(
            text=page,
            reply_markup=create_keyboard(
                KEYBOARDS_LEXICON['prev'],
                f'{number}/{last_number}',
                KEYBOARDS_LEXICON['next']
            )
        )

    else:
        await callback.message.edit_text(
            text=HANDLERS_LEXICON['delete_bookmark'],
            reply_markup=create_keyboard_bookmarks(*bookmarks)
        )


@router.callback_query(IsBookmarks())
async def add_bookmark_command(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    bookmark = add_bookmark(
        callback,
        storage,
        user_books
    )

    await state.update_data(storage)
    if bookmark:
        await callback.answer(
            text=f'Закладка {bookmark.split()[0]} добавлена'
        )
    else:
        await callback.answer(
            text='Закладка уже есть'
        )


@router.callback_query(MoveToBookmark())
async def process_move_to_bookmark(callback: CallbackQuery, state: FSMContext):

    storage = await state.get_data()
    number, last_number, page = move_to_bookmark(
        callback,
        storage,
        user_books,
    )
    await state.update_data(storage)

    await callback.message.edit_text(
        text=page,
        reply_markup=create_keyboard(
            KEYBOARDS_LEXICON['prev'],
            f'{number}/{last_number}',
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
