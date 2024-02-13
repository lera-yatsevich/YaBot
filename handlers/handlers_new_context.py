from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery

from states.states import FSMFillForm
from lexicon.lexicon import lexicon

from dbase.connect import createContext

from chat.answer import getAnswer

from keyboard.keyboard import createModelKeyboard, createContextKeyboard

router: Router = Router()

router.message.filter(StateFilter(FSMFillForm.new_name),
                      StateFilter(FSMFillForm.new_description))


# обработка названия нового контекста и вход в режим ввода описания контекста
@router.message(StateFilter(FSMFillForm.new_name))
async def process_new_context_name(message: Message,
                                   state: FSMContext):
    await state.update_data(context=message.text)

    await state.set_state(FSMFillForm.new_description)

    await message.answer(text=lexicon.get('new_context_description'))


# обработка описания нового контекста
@router.message(StateFilter(FSMFillForm.new_description))
async def process_new_context_descr(message: Message,
                                    state: FSMContext):

    data_prew = await FSMFillForm.new_name.get_data()

    createContext(data_prew['new_name'], message.text, message.chat.id)

    await state.set_state(FSMFillForm.auth)

    await message.answer(text=lexicon.get('new_context_saved'))
