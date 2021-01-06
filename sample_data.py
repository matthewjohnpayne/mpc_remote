import json

# --- EMPTY DICTS FOR TESTING -------------
def sample_test_dict():
    '''NB: The FunctionServer demands highly dictionary with certain keys, e.g. "test", ... '''
    return { 'test' : {'k':'v'} }
def sample_test_json_string():
    return json.dumps(sample_test_dict())


# --- DICTS FOR ORFIT-EXTENSION -------------
# --- EMPTY DICTS FOR TESTING -------------
def sample_orbfit_extension_input_json_string_empty():
    return json.dumps(sample_input_dict_empty())
    
def sample_orbfit_extension_input_dict_empty():
    return {
    "K15HI3Q": {
        "eq0dict": {},
        "rwodict": {},
        "obslist": [
            {},{}],
        }
    }

def sample_orbfit_extension_output_json_string_empty():
    return json.dumps(sample_output_dict_empty())

def sample_orbfit_extension_output_dict_empty():
    return {"K15HI3Q" : {  'obslist' :[{},{}],
                            'rwodict' : {},
                            'eq0dict' : {},
                            'eq1dict' : {},
                            'badtrkdict' : {} } }

# ----- POPULATED DATA  -------------------
def sample_orbfit_extension_input_json_string():
    return json.dumps(sample_orbfit_extension_input_dict())

def sample_orbfit_extension_input_dict():
    with open('testdict.json') as json_file:
        return json.load(json_file)
