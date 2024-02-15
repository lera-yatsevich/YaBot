from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from aiogram.types import Message

from states.states import FSMFillForm
from lexicon.lexicon import lexicon

from chat.answer import getAnswerInContext

router: Router = Router()

router.message.filter(StateFilter(FSMFillForm.context))


# Выход их контекста
@router.message(Command(commands='leave_context'))
async def process_context(message: Message, state: FSMContext):
    await state.set_data({})
    await state.set_state(FSMFillForm.auth)
    await message.answer(text=lexicon.get('/leave_context'))


# обработка команд общения с ботом в контексте
@router.message(Command(commands=['context', 'message']))
async def process_context_in_context(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('process_context_in_context'))


# Этот хэндлер будет отвечать на вопросы в чате
@router.message()
async def process_question(message: Message, state: FSMContext):
    data = await state.get_data()
    answer = getAnswerInContext(message.text, data['context'])
    await message.answer(text=answer)
