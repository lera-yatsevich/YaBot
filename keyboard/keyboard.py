from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def createModelKeyboard(models, curr_model=0):
    indicator = '⚪🟢'
    buttons = [[InlineKeyboardButton(text=f'{indicator[k==curr_model]} {v}',
                                     callback_data=f'model_{str(k)}')] for k, v in models.items()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def createContextKeyboard(context):
    buttons = [[InlineKeyboardButton(text=v,
                                     callback_data=f'context_{str(k)}')] for k, v in context.items()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
