import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery

from states.states import FSMFillForm
from lexicon.lexicon import lexicon

from dbase.connect import getUserParameters, getModelName
from dbase.connect import listOfModels
from dbase.connect import updateTemperature, updateMaxTokens, updateModel

from chat.answer import getAnswer

from keyboard.keyboard import createModelKeyboard

router: Router = Router()

router.message.filter(StateFilter(FSMFillForm.auth))


# Выводит текущие значения параметров
@router.message(Command(commands='parameters'))
async def process_parameters_command(message: Message, state: FSMContext):
    userParam = getUserParameters(message.chat.id)
    if userParam:
        modelParam = getModelName(userParam.get('model_id'))
        if modelParam:
            await message.answer(text=f"{lexicon.get('/parameters')}"
                                 f"model: {modelParam.get('model_name')}\n"
                                 f"temperature: {userParam.get('temperature')}\n"
                                 f"max_tokens: {userParam.get('max_tokens')}")
        else:
            await message.answer(text=lexicon.get('user_not_found'))
    else:
        await message.answer(text=lexicon.get('user_not_found'))

# Изменение температуры
@router.message(Command(commands='set_temperature'),
                F.text.regexp('/set_temperature ([0-9]*[.])?[0-9]+'))
async def process_set_temp_command(message: Message, state: FSMContext):
    temperature = float(re.findall("([0-9]*[.]?[0-9]+)", message.text)[0])
    updateTemperature(temperature, message.chat.id)
    await message.answer(text=lexicon.get('/set_temperature'))


# Изменение температуры (ошибочный формат)
@router.message(Command(commands='set_temperature'))
async def process_set_temp_command_err(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('set_temperature_format_err'))


# Изменение максимального числа токенов
@router.message(Command(commands='set_max_tokens'),
                F.text.regexp('/set_max_tokens [0-9]+'))
async def process_set_maxtokens_command(message: Message, state: FSMContext):
    max_tokens = float(re.findall("([0-9]+)", message.text)[0])
    updateMaxTokens(max_tokens, message.chat.id)
    await message.answer(text=lexicon.get('/set_max_tokens'))


# Изменение максимального числа токенов (ошибочный формат)
@router.message(Command(commands='set_max_tokens'))
async def process_set_maxtokens_command_err(message: Message,
                                            state: FSMContext):
    await message.answer(text=lexicon.get('set_max_token_format_err'))


# Изменение модели
@router.message(Command(commands='set_model'), StateFilter(FSMFillForm.auth))
async def process_set_model_command(message: Message, state: FSMContext):
    models = listOfModels()
    curr_model = getUserParameters(message.chat.id).get('model_id')
    keyboard = createModelKeyboard(models, curr_model)
    await message.answer(text=lexicon.get('/set_model'),
                         reply_markup=keyboard)

# Обработка клавиатуры с моделями
@router.callback_query(F.data.contains('model_'))
async def process_buttons_model(callback: CallbackQuery):
    model_id = int(re.findall("([0-9]+)", callback.data)[0])
    updateModel(model_id, callback.message.chat.id)
    await callback.message.edit_text(
        text=lexicon.get('set_model_done'))


# Отправка единичного сообщения в ChatGPT
@router.message(Command(commands='message'))
async def process_message_command(message: Message, state: FSMContext):
    await message.answer(text=getAnswer(
        message.text.replace('/message', '').strip()))
