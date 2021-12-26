def get_module_resource():
    from importlib import resources as importlib_resources
    import json
    file = importlib_resources.open_text('my_skb_mod.submod', 'module_resource.json')
    data = json.load(file)
    return data
