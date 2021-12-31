import json
import jq
from enums import ProductTypeId
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError

"""Analyse the definition of the deals in order to determine valid menu combination"""

toppings = {}
with open('toppings.json', 'r') as f:
    topping_data = json.load(f)['data']
    toppings = {t["toppingId"]: t["title"] for t in topping_data}
    toppings.update({t["title"]: t["toppingId"] for t in topping_data})

dips = {}
with open('products.json', 'r') as f:
    dips_data = json.load(f)['data']
    dips = {d['productSKU']["sku"]: d['title'] for d in dips_data if d['name'] == 'Dips'}


def get_topping_from_id(id):
    try:
        return toppings[id]
    except KeyError:
        ...


def get_products_from_deal(deal):
    # check it can be delivered
    if deal["carryoutOnlyFlag"] and not deal["deliveryOnlyFlag"]:
        print("Can't get deal for delivery")
        return

    steps = deal['steps']
    products = []
    for step in steps:
        choices = step['choices']
        raw_type_id = jq.compile('.[1].products[0].productSKU.productTypeId').input(choices).first()
        product_type_id = ProductTypeId.GetProductType(raw_type_id)
        product_type_name = product_type_id.GetDisplayName()

        prompt_choices = [{
            'type': 'list',
            'name': 'id',
            'message': f"Choose {product_type_name}",
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

        # with the product, handle its 'instructions', if it has any
        if 'instructionList' in product and product['instructionList']:
            available_instructions = product['instructionList']
            instructions = []
            for instruction in available_instructions:
                prompt_instruction = [{'type': 'list', 'name': 'id', 'message': instruction['name'],
                                       'choices': [{
                                           'name': x['name'],
                                           'value': x['id']
                                       } for x in instruction['instructions']]}]
                response = prompt(questions=prompt_instruction)
                instructions.append((instruction['id'], response['id']))
            product['_instruction_responses'] = instructions
            print(product['_instruction_responses'])

        # ignore possible sauces, since it seems that papa johns only has a standard base sauce available for all pizzas

        # process the possible toppings for the product
        # TODO: enable selecting topping quantity with extended pyinquirer checkbox feature
        if 'allowedToppings' in product and product['allowedToppings']:
            prompt_toppings = [{'type': 'checkbox', 'name': 'selected_toppings', 'message': 'Which toppings?',
                                'choices': [{
                                    'name': str(toppings[x['toppingId']]),
                                    'value': str(toppings[x['toppingId']]),
                                    'checked': x['toppingId'] in product['defaultToppings']
                                } for x in product['allowedToppings'] if x["toppingId"] in toppings]}]
            response = prompt(questions=prompt_toppings)
            product['_toppings'] = [toppings[x] for x in response['selected_toppings']]
            print(product['_toppings'])

        # finally, let's see if there are any complimentary sides to choose from
        if 'complimentarySides' in product and product['complimentarySides']:

            available_sides = product['complimentarySides']
            chosen_sides = []
            for side in available_sides:
                prompt_side = [
                    {'type': 'list', 'name': 'id', 'message': f"Complimentary side {side['complimentarySideId']}",
                     'default': side['defaultProduct']['sku'],
                     'choices': [{
                         'name': dips[x['sku']],
                         'value': x['sku'],
                     } for x in side['productChoices']]}]
                response = prompt(questions=prompt_side)
                chosen_sides.append(response['id'])

            product['_complimentary_sides'] = chosen_sides
            print(product['_complimentary_sides'])

        products.append(product)

    return products


with open('feed_fam.json', 'r') as f:
    products = get_products_from_deal(json.load(f)['data'])
    print(products)
