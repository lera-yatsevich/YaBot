import json

text = r'''{
    "id": "cmpl-8qQ1ncPqU4C43gXvMcEZ5UbUu0n31",
    "object": "text_completion",
    "created": 1707503799,
    "model": "gpt-3.5-turbo-instruct",
    "choices": [
        {
            "text": "\n\nIt is not appropriate to limit people's use of technology. Technology has become an integral part of our daily lives and has numerous benefits, such as facilitating communication, increasing efficiency, and providing access to information. Instead of limiting its use, it is important to educate individuals on responsible and safe use of technology. This can include setting boundaries for screen time, teaching digital etiquette, and promoting a healthy balance between technology use and other activities. It is also important to address any negative effects of technology, such as addiction or cyberbullying, through proper education and support. Ultimately, it is up to individuals to manage their own use of technology, and it is not productive to impose restrictions on its use.",
            "index": 0,
            "logprobs": null,
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 12,
        "completion_tokens": 140,
        "total_tokens": 152
    }
}'''


def getAnswer(question):

    answ = json.loads(text)

    # self.date = answ['created']
    # self.content = answ['choices'][0]['text']

    return answ['choices'][0]['text']


# class messageAnswer():
#     def __init__(self, answer=text) -> None:
#         answ = json.loads(answer)
#         self.date = answ['created']
#         self.content = answ['choices'][0]['text']

#     def __str__(self) -> str:
#         return self.content

# a = chatAnswer(answer=text)

# print(a)