import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, Command
from aiogram.types import Message, CallbackQuery


from states.states import FSMFillForm
from lexicon.lexicon import lexicon

from dbase.connect import getContextName, listOfContexts, deleteContext

from keyboard.keyboard import createKeyboard

router: Router = Router()
router.message.filter(StateFilter(FSMFillForm.auth))


# вход в контекст
@router.message(Command(commands='context'))
async def process_context(message: Message, state: FSMContext):
    contexts = listOfContexts(message.chat.id)
    keyboard = createKeyboard({**contexts,
                               'create': lexicon.get('create_context'),
                               'delete': lexicon.get('delete_context')},
                               prefix='context_')
    await message.answer(text=lexicon.get('/context'),
                         reply_markup=keyboard)


# Обработка клавиатуры с контекстом - вариант удаления контекста
@router.callback_query(F.data.contains('context_delete'))
async def process_buttons_context_delete(callback: CallbackQuery,
                                         state: FSMContext):

    contexts = listOfContexts(callback.message.chat.id)
    keyboard = createKeyboard(contexts, prefix='delete_')
    await callback.message.edit_text(text=lexicon.get('if_delete_context'),
                                     reply_markup=keyboard)


# Обработка клавиатуры с контекстом - вариант создания контекста
@router.callback_query(F.data.contains('context_create'))
async def process_buttons_context_create(callback: CallbackQuery,
                                         state: FSMContext):

    await state.set_state(FSMFillForm.new_name)

    await callback.message.edit_text(text=lexicon.get('new_context_name'))


# Обработка клавиатуры с контекстом - вариант контекста
@router.callback_query(F.data.contains('context_'),
                       F.data.regexp(r"context_(\d+)").as_("num")
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

    await callback.message.edit_text(
        text=f"{lexicon.get('context_deleted') % (context_name)}"
        )


# техническая команда для сброса состояния
@router.message(Command(commands='reset'))
async def process_reset_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=lexicon.get('/reset'))
