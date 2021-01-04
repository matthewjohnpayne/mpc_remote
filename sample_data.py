import json

# --- EMPTY DICTS FOR TESTING -------------
def sample_test_dict():
    '''NB: The FunctionServer demands highly dictionary with certain keys, e.g. "test", ... '''
    return { 'test' : {} }


# --- ???????????????????????? -------------

def sample_output_json_string_empty():
    return json.dumps(sample_output_dict_empty())

def sample_output_dict_empty():
    return {"K15HI3Q" : {  'obslist' :[{},{}],
                            'rwodict' : {},
                            'eq0dict' : {},
                            'eq1dict' : {},
                            'badtrkdict' : {} } }

# --- EMPTY DATA STRUCTURE ----------------
def sample_input_json_string_empty():
    return json.dumps(sample_input_dict_empty())
    
def sample_input_dict_empty():
    return {
    "K15HI3Q": {
        "eq0dict": {},
        "rwodict": {},
        "obslist": [
            {},{}],
        }
    }

# ----- POPULATED DATA  -------------------
def sample_input_json_string():
    return json.dumps(sample_input_dict())


def sample_input_dict():
    with open('testdict.json') as json_file:
        return json.load(json_file)
