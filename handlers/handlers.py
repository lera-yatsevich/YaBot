from aiogram import Router

from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter

from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import default_state

from states.states import FSMFillForm
from lexicon.lexicon import lexicon
from dbase.connect import registerUser, authRequest


router: Router = Router()


# Срабатывает на команду /start в дефолтном состоянии
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


# если пользователь не авторизован
@router.message(~StateFilter(FSMFillForm.auth))
async def process_auth_err(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('not_auth'))


# Этот хэндлер будет срабатывать в всех непонятных случаях
@router.message()
async def send_echo(message: Message, state: FSMContext):
    await message.reply(text=lexicon.get('trap'))
