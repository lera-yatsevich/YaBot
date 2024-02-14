from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery

from states.states import FSMFillForm
from lexicon.lexicon import lexicon

from dbase.connect import getUserParameters, getModelName
from dbase.connect import listOfModels
from dbase.connect import updateTemperature, updateMaxTokens, updateModel

from chat.answer import getAnswer, getAnswerInContext

from keyboard.keyboard import createModelKeyboard

router: Router = Router()

router.message.filter(StateFilter(FSMFillForm.context))


# Выход их контекста
@router.message(Command(commands='leave_context'))
async def process_context(message: Message, state: FSMContext):
    await state.set_data({})
    await state.set_state(FSMFillForm.auth)
    await message.answer(text=lexicon.get('/leave_context'))


# Этот хэндлер будет отвечать на вопросы в чате
@router.message()
async def process_question(message: Message, state: FSMContext):
    data = await state.get_data()
    # print(data)
    answer = getAnswerInContext(message.text, data['context'])
    await message.answer(text=answer)
