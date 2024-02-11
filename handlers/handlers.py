import re
from environs import Env

from aiogram import Dispatcher, F

from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter, Command

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.redis import RedisStorage, Redis

from states.states import FSMFillForm
from lexicon.lexicon import lexicon
from dbase.connect import getUserParameters, getModelName
from dbase.connect import postgresParams, listOfModels
from dbase.connect import registerUser, authRequest
from dbase.connect import updateTemperature, updateMaxTokens, updateModel

from chat.answer import getAnswer
from keyboard.keyboard import createModelKeyboard

redis: Redis = Redis(host='localhost')

env = Env()
env.read_env('../env/.env')

dbaseParams = postgresParams(host='localhost',
                             user='admin',
                             password=env('POSTGRES_PASSWORD'))

# Инициализируем хранилище (создаем экземпляр класса RedisStorage)
storage: RedisStorage = RedisStorage(redis=redis)

dp: Dispatcher = Dispatcher(storage=storage)


# Срабатывает на команду /start в дефолтном состоянии
# и выводит описания команд, если прошла авторизация
@dp.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    registerUser(dbaseParams,
                 message.from_user.id,
                 message.from_user.first_name,
                 message.from_user.last_name,
                 message.from_user.username)
    if authRequest(dbaseParams, message.chat.id):
        await state.set_state(FSMFillForm.auth)
        await message.answer(text=lexicon.get('/start'))
    else:
        await message.answer(text=lexicon.get('auth_failed'))
    # await state.set_state(FSMFillForm.answ_name)


# если пользователь не авторизован
@dp.message(Command(commands=['parameters',
                              'set_temperature',
                              'set_max_tokens',
                              'set_model',
                              'message']),
            ~StateFilter(FSMFillForm.auth))
async def process_auth_err(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('not_auth'))


# Выводит текущие значения параметров
@dp.message(Command(commands='parameters'), StateFilter(FSMFillForm.auth))
async def process_parameters_command(message: Message, state: FSMContext):
    userParam = getUserParameters(dbaseParams, message.chat.id)
    if userParam:
        modelParam = getModelName(dbaseParams, userParam.get('model_id'))
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
@dp.message(Command(commands='set_temperature'),
            F.text.regexp('/set_temperature ([0-9]*[.])?[0-9]+'),
            StateFilter(FSMFillForm.auth))
async def process_set_temp_command(message: Message, state: FSMContext):
    temperature = float(re.findall("([0-9]*[.]?[0-9]+)", message.text)[0])
    updateTemperature(dbaseParams, temperature, message.chat.id)
    await message.answer(text=lexicon.get('/set_temperature'))


# Изменение температуры (ошибочный формат)
@dp.message(Command(commands='set_temperature'),
            StateFilter(FSMFillForm.auth))
async def process_set_temp_command_err(message: Message, state: FSMContext):
    await message.answer(text=lexicon.get('set_temperature_format_err'))


# Изменение максимального числа токенов
@dp.message(Command(commands='set_max_tokens'),
            F.text.regexp('/set_max_tokens [0-9]+'),
            StateFilter(FSMFillForm.auth))
async def process_set_maxtokens_command(message: Message, state: FSMContext):
    max_tokens = float(re.findall("([0-9]+)", message.text)[0])
    updateMaxTokens(dbaseParams, max_tokens, message.chat.id)
    await message.answer(text=lexicon.get('/set_max_tokens'))


# Изменение максимального числа токенов (ошибочный формат)
@dp.message(Command(commands='set_max_tokens'), StateFilter(FSMFillForm.auth))
async def process_set_maxtokens_command_err(message: Message,
                                            state: FSMContext):
    await message.answer(text=lexicon.get('set_max_token_format_err'))


# Изменение модели
@dp.message(Command(commands='set_model'), StateFilter(FSMFillForm.auth))
async def process_set_model_command(message: Message, state: FSMContext):
    models = listOfModels(dbaseParams)
    curr_model = getUserParameters(dbaseParams,
                                   message.chat.id).get('model_id')
    keyboard = createModelKeyboard(models, curr_model)
    await message.answer(text=lexicon.get('/set_model'),
                         reply_markup=keyboard)


# Обработка клавиатуры с моделями
@dp.callback_query(F.data.contains('model_'), StateFilter(FSMFillForm.auth))
async def process_buttons_model(callback: CallbackQuery):
    model_id = int(re.findall("([0-9]+)", callback.data)[0])
    updateModel(dbaseParams, model_id, callback.message.chat.id)
    await callback.message.edit_text(
        text=lexicon.get('set_model_done'))


# Отправка единичного сообщения в ChatGPT
@dp.message(Command(commands='message'), StateFilter(FSMFillForm.auth))
async def process_message_command(message: Message, state: FSMContext):
    await message.answer(text=getAnswer(
        message.text.replace('/message', '').strip()))


# техническая команда для сброса состояния
@dp.message(Command(commands='reset'))
async def process_reset_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=lexicon.get('/reset'))


# Этот хэндлер будет срабатывать в всех непонятных случаях
@dp.message()
async def send_echo(message: Message, state: FSMContext):
    await message.reply(text=lexicon.get('trap'))
