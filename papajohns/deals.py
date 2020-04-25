import json
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError

"""Analyse the definition of the deals in order to determine valid menu combination"""


def get_products_from_deal(deal):
    # check it can be delivered
    if deal["carryoutOnlyFlag"] and not deal["deliveryOnlyFlag"]:
        print("Can't get deal for delivery")
        return

    products = []
    steps = deal['steps']
    for step in steps:
        choices = step['choices']
        prompt_choices = [{
            'type': 'list',
            'name': 'id',
            'message': f"Item {step['sortOrder']}",
            'choices': [{
                'name': f"{x['title']} - {x['shortDescription']}",
                'value': x['productGroupId'],
                'short': f"{x['title']}"} for x in choices]
        }]
        product_group = prompt(questions=prompt_choices)

        base_ingredients = \
            [x['availableBaseIngredientTypes'] for x in choices if x['productGroupId'] == product_group['id']][0]
        prompt_base_ingredients = [{'type': 'list', 'name': 'id', 'message': 'Base',
                                    'choices': [{
                                        'name': x['name'],
                                        'value': x['id']
                                    } for x in base_ingredients]}]
        base_ingredient = prompt(questions=prompt_base_ingredients)

        sizes = \
            [x['availableSizeTypes'] for x in choices if x['productGroupId'] == product_group['id']][0]
        prompt_sizes = [{'type': 'list', 'name': 'id', 'message': 'Size',
                         'choices': [{
                             'name': x['name'],
                             'value': x['id']
                         } for x in sizes]}]
        size = prompt(questions=prompt_sizes)

        # with base and size, we can lookup the product within the product group id that the user actually wants
        product = None
        product_group_products = [x['products'] for x in choices if x['productGroupId'] == product_group['id']][0]
        for product_group_product in product_group_products:
            if product_group_product['productSKU']['baseIngredientTypeId'] == base_ingredient['id'] and \
                    product_group_product['productSKU']['baseIngredientSizeId'] == size['id']:
                product = product_group_product
        products.append(product)
