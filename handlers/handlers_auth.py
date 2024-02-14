import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery

from states.states import FSMFillForm
from lexicon.lexicon import lexicon

from dbase.connect import getUserParameters, getModelName, getContextName
from dbase.connect import listOfModels, listOfContexts
from dbase.connect import updateTemperature, updateMaxTokens, updateModel
from dbase.connect import deleteContext

from chat.answer import getAnswer

from keyboard.keyboard import createModelKeyboard, createContextKeyboard

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


# вход в контекст
@router.message(Command(commands='context'))
async def process_context(message: Message, state: FSMContext):
    contexts = listOfContexts(message.chat.id)
    keyboard = createContextKeyboard({**contexts,
                                      'create_context': lexicon.get('create_context'),
                                      'delete_context': lexicon.get('delete_context')},
                                      prefix='context_')
    await message.answer(text=lexicon.get('/context'),
                         reply_markup=keyboard)


# Обработка клавиатуры с контекстом - вариант удаления контекста
@router.callback_query(F.data.contains('delete_context'))
async def process_buttons_context_delete(callback: CallbackQuery,
                                         state: FSMContext):

    contexts = listOfContexts(callback.message.chat.id)
    keyboard = createContextKeyboard(contexts, prefix='delete_')
    await callback.message.edit_text(text=lexicon.get('if_delete_context'),
                                     reply_markup=keyboard)


# Обработка клавиатуры с контекстом - вариант создания контекста
@router.callback_query(F.data.contains('create_context'))
async def process_buttons_context_create(callback: CallbackQuery,
                                         state: FSMContext):

    await state.set_state(FSMFillForm.new_name)

    await callback.message.edit_text(text=lexicon.get('new_context_name'))


# Обработка клавиатуры с контекстом - вариант контекста
@router.callback_query(F.data.contains('context_'),
                    #    F.data.regexp(r"context_(\d+)").as_("num")
                       )
async def process_buttons_context_choose(callback: CallbackQuery,
                                         state: FSMContext):
    # print(f"{F.text=}, {F.text=='delete_context'}")
    # print(f'{num=}')
    context_id = int(re.findall("([0-9]+)", callback.data)[0])

    await state.set_state(FSMFillForm.context)
    await state.update_data(context=context_id)

    # await state.get_data()

    await callback.message.edit_text(
        text=lexicon.get('set_context_done'))

    await callback.message.answer(text=f"{lexicon.get('current_context')} "
                                  f'"{getContextName(context_id)}". \n\n'
                                  f"{lexicon.get('how_to_leave')}")


# Обработка клавиатуры с выбором контекста для удаления
@router.callback_query(F.data.contains('delete_'))
async def process_buttons_del_choose(callback: CallbackQuery,
                                     state: FSMContext):

    context_id = int(re.findall("([0-9]+)", callback.data)[0])

    context_name = getContextName(context_id)

    deleteContext(context_id)

    await callback.message.edit_text(text=f"{lexicon.get('context_deleted')} "
                                     f'"{context_name}" {lexicon.get("context_deleted_2")}')


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
@router.message(Command(commands='set_model'))
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


# техническая команда для сброса состояния
@router.message(Command(commands='reset'))
async def process_reset_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=lexicon.get('/reset'))
