from aiogram import Router

from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter, Command

from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import default_state

from states.states import FSMFillForm
from lexicon.lexicon import lexicon
from dbase.connect import registerUser, authRequest
from dbase.connect import setOfAdmins, getUserParameters


router: Router = Router()


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


# обработка команды админ для не админов
@router.message(Command(commands='admin'))
async def process_not_admin(message: Message, state: FSMContext):

    await message.answer(text=lexicon.get('not_admin')+'\n'.join(
        [f"@{getUserParameters(admin_id)['username']}" for admin_id in setOfAdmins()])
        )


# если пользователь не авторизован
@router.message(~StateFilter(FSMFillForm.auth))
async def process_auth_err(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('not_auth'))


# leave_context вне контекста
@router.message(Command(commands='leave_context'))
async def process_leave_context_outside(message: Message, state: FSMContext):

    await message.answer(text=lexicon.get('leave_context_context_outside'))


# Этот хэндлер будет срабатывать в всех непонятных случаях
@router.message()
async def process_whatever(message: Message, state: FSMContext):
    await message.reply(text=lexicon.get('trap'))
