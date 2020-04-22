#!/usr/bin/env python3

from __future__ import print_function, unicode_literals

import asyncio

import regex
from papajohns.api import Api

from pprint import pprint
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#673AB7 bold',
    Token.Instruction: '',  # default
    Token.Answer: '#2196f3 bold',
    Token.Question: '',
})


class PostCodeValidator(Validator):
    def validate(self, document):
        ok = True
        if not ok:
            raise ValidationError(message='Invalid postcode',
                                  cursor_position=len(document.text))


class PhoneNumberValidator(Validator):
    def validate(self, document):
        ok = regex.match(
            '^([01]{1})?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\s?((?:#|ext\.?\s?|x\.?\s?){1}(?:\d+)?)?$',
            document.text)
        if not ok:
            raise ValidationError(
                message='Please enter a valid phone number',
                cursor_position=len(document.text))  # Move cursor to end


class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end


async def main():
    print('Hi, welcome to Python Pizza')

    api = Api()

    questions = [
        {
            'type': 'confirm',
            'name': 'forDelivery',
            'message': 'Is this for delivery?',
            'default': True
        },
        {
            'type': 'input',
            'name': 'postcode',
            'message': 'What\'s your post code?',
            'default': 'po48ap',
            'filter': lambda val: val.upper(),
            'validate': PostCodeValidator
        },
        # {
        #     'type': 'list',
        #     'name': 'size',
        #     'message': 'What size do you need?',
        #     'choices': ['Large', 'Medium', 'Small'],
        #     'filter': lambda val: val.lower()
        # },
        # {
        #     'type': 'input',
        #     'name': 'quantity',
        #     'message': 'How many do you need?',
        #     'validate': NumberValidator,
        #     'filter': lambda val: int(val)
        # },
        # {
        #     'type': 'expand',
        #     'name': 'toppings',
        #     'message': 'What about the toppings?',
        #     'choices': [
        #         {
        #             'key': 'p',
        #             'name': 'Pepperoni and cheese',
        #             'value': 'PepperoniCheese'
        #         },
        #         {
        #             'key': 'a',
        #             'name': 'All dressed',
        #             'value': 'alldressed'
        #         },
        #         {
        #             'key': 'w',
        #             'name': 'Hawaiian',
        #             'value': 'hawaiian'
        #         }
        #     ]
        # },
        # {
        #     'type': 'rawlist',
        #     'name': 'beverage',
        #     'message': 'You also get a free 2L beverage',
        #     'choices': ['Pepsi', '7up', 'Coke']
        # },
        # {
        #     'type': 'input',
        #     'name': 'comments',
        #     'message': 'Any comments on your purchase experience?',
        #     'default': 'Nope, all good!'
        # },
        # {
        #     'type': 'list',
        #     'name': 'prize',
        #     'message': 'For leaving a comment, you get a freebie',
        #     'choices': ['cake', 'fries'],
        #     'when': lambda answers: answers['comments'] != 'Nope, all good!'
        # }
    ]

    delivery = prompt(questions, style=style)
    address_choices = await api.get_addresses(delivery['postcode'])
    address = prompt(questions=[{
        'type': 'list',
        'name': 'address1',
        'message': 'What is your address?',
        'choices': [x['address1'] for x in address_choices]
    }])
    full_address = [x for x in address_choices if x['address1'] == address['address1']][0]

    delivery_stores = await api.get_delivery_stores(full_address)
    store_address = prompt(questions=[{
        'type': 'list',
        'name': 'address1',
        'message': 'Which delivery store?',
        'choices': [x['storeLocation']['address1'] for x in delivery_stores]
    }])
    store_id = [x['storeId'] for x in delivery_stores if x['storeLocation']['address1'] == store_address['address1']][0]

    store_deals = await api.get_store_deals(store_id)
    store_deal = prompt(questions=[{
        'type': 'list',
        'name': 'title',
        'message': 'Which deal?',
        'choices': [x['title'] for x in store_deals]
    }])
    deal_id = [x['dealId'] for x in store_deals if x['title'] == store_deal['title']][0]



    del api


if __name__ == '__main__':
    asyncio.run(main())
