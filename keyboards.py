from aiogram import Bot
from aiogram.types import BotCommand, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon import COMMAND_LEXICON


async def set_main_menu(bot: Bot) -> None:
    bot_commands = [
        BotCommand(command=command, description=description)
        for command, description in COMMAND_LEXICON.items()
    ]
    await bot.set_my_commands(bot_commands)


def create_books_keyboard(*books):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        *[InlineKeyboardButton(text=button, callback_data=f'book-{key}')
          for key, button in enumerate(books, start=1)],
        width=1
    )
    return kb_builder.as_markup()


def create_keyboard(*buttons, width=None):
    if width is None:
        width = len(buttons)
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        *[InlineKeyboardButton(text=button, callback_data=button)
          for button in buttons],
        width=width
    )
    return kb_builder.as_markup()


def create_keyboard_bookmarks(*buttons):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        *[InlineKeyboardButton(text=button, callback_data=button.split()[0])
          for button in buttons],
        width=1
    )
    if buttons:
        kb_edit_bookmarks = InlineKeyboardButton(
            text='Редактировать',
            callback_data='edit_bookmarks'
        )
        kb_builder.row(kb_edit_bookmarks)
    return kb_builder.as_markup()


def create_keyboard_del_bookmarks(*buttons):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        *[InlineKeyboardButton(
            text=button,
            callback_data=f'{button.split()[0]} {button.split()[-1]}'
        )
         for button in buttons],
        width=1
    )
    if buttons:
        kb_edit_bookmarks = InlineKeyboardButton(
            text='Отмена',
            callback_data='cancel'
        )
        kb_builder.row(kb_edit_bookmarks)
    return kb_builder.as_markup()
