import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from lexicon.lexicon import lexicon

from dbase.connect import setOfAdmins, listOfUsers, updateUserAdmission
from dbase.connect import getUserParameters

from keyboard.keyboard import createKeyboard

router: Router = Router()

router.message.filter(lambda message: message.from_user.id in setOfAdmins())


@router.message(Command(commands='admin'))
async def process_admin(message: Message, state: FSMContext):
    keyboard = createKeyboard({'add': lexicon.get('user_add'),
                               'remove': lexicon.get('user_remove')},
                               prefix='user_')
    await message.answer(text=lexicon.get('/admin'),
                         reply_markup=keyboard)


# Выбор пользователя для добавления
@router.callback_query(F.data.contains('user_add'))
async def process_buttons_user_add(callback: CallbackQuery):

    userList = listOfUsers(is_admitted=False)

    if len(userList):
        keyboard = createKeyboard(userList, prefix='useradd_')

        await callback.message.edit_text(
            text=lexicon.get('choose_user_to_add'),
            reply_markup=keyboard)

    else:
        await callback.message.edit_text(
            text=lexicon.get('nothing_to_add'))


# Выбор пользователя для удаления
@router.callback_query(F.data.contains('user_remove'))
async def process_buttons_user_remove(callback: CallbackQuery):

    userList = listOfUsers(is_admitted=True)

    if len(userList):
        keyboard = createKeyboard(userList,
                                  prefix='userremove_')

        await callback.message.edit_text(
            text=lexicon.get('choose_user_to_remove'),
            reply_markup=keyboard)

    else:
        await callback.message.edit_text(
            text=lexicon.get('nothing_to_remove'))


# Удаление выбранного пользователя
@router.callback_query(F.data.contains('userremove_'))
async def process_buttons_remove(callback: CallbackQuery):

    user_id = int(re.findall("([0-9]+)", callback.data)[0])
    updateUserAdmission(user_id, is_admitted=False)

    user_name = getUserParameters(user_id)['username']

    await callback.message.edit_text(
        text=lexicon.get('user_removed') % (user_name))


# Добавление выбранного пользователя
@router.callback_query(F.data.contains('useradd_'))
async def process_buttons_add(callback: CallbackQuery):

    user_id = int(re.findall("([0-9]+)", callback.data)[0])
    updateUserAdmission(user_id, is_admitted=True)

    user_name = getUserParameters(user_id)['username']

    await callback.message.edit_text(
        text=lexicon.get('user_added') % (user_name))
