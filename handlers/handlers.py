from aiogram import Router

from aiogram.types import Message
from aiogram.filters import StateFilter, Command

from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import default_state

from states.states import FSMFillForm
from lexicon.lexicon import lexicon
from dbase.connect import setOfAdmins, getUserParameters


router: Router = Router()


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
