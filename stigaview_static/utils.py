def update_dict_list(d: dict, key: str, value: object) -> dict:
    if key not in d.keys():
        d[key] = list()
    d[key].append(value)
    return d
