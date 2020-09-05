def get_products(query_set):
    product_models = {}
    product_models_set = set()
    item_set = set()
    for item in query_set:
        for model in item.model_id.all():
            if item not in product_models:
                product_models[item] = []
            product_models[item].append(model)
            product_models[item].sort(key=lambda x: [x.family_id.family_name])
            product_models_set.add(model)
        item_set.add(item)
    return len(item_set), len(product_models_set), product_models


def get_error(tip_query_set, man_query_set):
    error_dict = {}
    for item in tip_query_set:
        for tip in item.techtipfix_set.all():
            if item not in error_dict:
                error_dict[item] = []
            error_dict[item].append(tip)
            error_dict[item].sort(key=lambda x: [x.tech_tip_number])
    for item in man_query_set:
        for fix in item.manualfix_set.all():
            if item not in error_dict:
                error_dict[item] = []
            error_dict[item].append(fix)
    return {key: error_dict[key] for key in sorted(error_dict.keys(), key=lambda x: x.error_name)}


def alphanumeric_generator(length=8):
    import uuid
    import random

    alpha_num = str(uuid.uuid4()).upper().replace('-', '')
    start = random.randint(0, 32-length)
    return alpha_num[start:start+length]
