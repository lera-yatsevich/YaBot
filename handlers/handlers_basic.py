from aiogram import Router

from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import default_state

from states.states import FSMFillForm
from lexicon.lexicon import lexicon
from dbase.connect import registerUser, authRequest

router: Router = Router()


# техническая команда для сброса состояния
@router.message(Command(commands='reset'))
async def process_reset_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=lexicon.get('/reset'))


# Срабатывает на команду /start в любом состоянии
# и выводит описания команд, если прошла авторизация
@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    registerUser(message.from_user.id,
                 message.from_user.first_name,
                 message.from_user.last_name,
                 message.from_user.username)
    if authRequest(message.chat.id):
        await state.set_state(FSMFillForm.auth)
        await message.answer(text=lexicon.get('/start'))
    else:
        await message.answer(text=lexicon.get('auth_failed'))
