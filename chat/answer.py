from environs import Env
from openai import OpenAI

from dbase.connect import getContext, updateContext, getModelName
from dbase.connect import getUserParameters, getUserfromContext

from chat.role import role

env = Env()
env.read_env('../env/.env')


def gptRequestInContext(context_id):
    client = OpenAI(
        api_key=env('OPENAI_TOKEN'),
    )

    userId = getUserfromContext(context_id)

    messages = getContext(context_id)

    parameters = getUserParameters(userId)

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=getModelName(parameters.get('model_id')),
        max_tokens=parameters.get('max_tokens'),
        temperature=parameters.get('temperature'),
        n=1
    )
    answ = chat_completion.choices[0].message.content

    return answ


def getAnswerInContext(question, context_id):

    updateContext(context_id, question, role.USER)
    answer = gptRequestInContext(context_id)
    updateContext(context_id, answer, role.ASSISTANT)

    return answer
