from otree.api import *


doc = """
shared_functions:
"""


class C(BaseConstants):
    NAME_IN_URL = 'shared_functions'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    pass


################################ FUNCTIONS ################################

# ============ Time Styles ============ #

def set_expiration_time(minutes_for_task, is_minutes): # sets the time at which X expires; expiry = set_expiration_time()
    import time
    if is_minutes == True:
        expiry = time.time() + minutes_for_task*60
    else:
        expiry = time.time() + minutes_for_task
    return expiry

# def get_timeout_seconds(expiry): # time left until expiration; time_remaining = get_timeout_seconds(expiry)
#     import time
#     return expiry - time.time()

def get_time_from_start(minutes_for_task, expiry, is_minutes): # time elapsed since the start of the timer. # print(make_it_base_sixty(get_time_from_start(MINUTES_FOR_TASK, expiry),k))
    import time
    if is_minutes == True:
        return minutes_for_task*60 - (expiry - time.time())
    else:
        return minutes_for_task - (expiry - time.time())
    
def addZero(obj): # based on js_scipt function of this name
    if (obj < 10):
        obj = str(obj)
        obj = "0" + obj
    return str(obj)

def make_it_base_sixty(time_remaining, place): # place is 1:6 where 6 is double-digit hours, and 1 is single-digit seconds. precision of the time. i.e., 65:43:21. print(make_it_base_sixty(time_remaining, k))
    import math
    hLeft = math.floor(time_remaining/3600)
    mLeft = math.floor((time_remaining - hLeft*3600)/60)
    sLeft = math.trunc(time_remaining - math.floor(time_remaining/60)*60)
    x = 3 - math.ceil(place/2)
    if place == 6:
        h = addZero(hLeft)
    else:
        h = str(hLeft)
    if place == 4:
        m = addZero(mLeft)
    else:
        m = str(mLeft)
    if place == 2:
        s = "0:" + addZero(sLeft)
    else:
        s = str(sLeft)
    possible_displays = [h + ":" + addZero(mLeft) + ":" + addZero(sLeft),
                         m + ":" + addZero(sLeft),
                         s]
    if time_remaining < 0:
        display_time =  'time\'s up'
    else:
        display_time = possible_displays[x]
    return display_time
# e.g.,: 
    # for k in range(1,7):
    #   print(make_it_base_sixty(get_time_from_start(MINUTES_FOR_TASK, expiry),k))
    # 26
    # 0:26
    # 7:26
    # 07:26
    # 0:07:26
    # 00:07:26


# ============ Data Handling ============ #

# record a dictionary as a json object (ideal for use with models.LongStringfield so that you can save a dictionary to a player model; poorman's version of ExtraModel)
def record_json_obj(the_dict):
    import json
    jsonObj = json.dumps(the_dict)
    return jsonObj

# retrieve a json object so that python can read it (ideally retrieves the dictionary you saved using record_json_obj, but also good with javascript dictionaries)
    # can turn lists of numbers that were saved as a string into a list of integers
def recall_json_obj(the_obj, sorted):
    import json
    pythonObj = json.loads(the_obj)
    if sorted == True:
        pythonObj.sort()
    return pythonObj
# e.g., 
    # if the_obj = string_num_list =  '[5, 4, 3]'
    # recall_json_obj(string_num_list, True)
    # [3, 4, 5]


# ============ Randomization and Reordering ============ #

def randomize_order(data, extras): # ~~~ randomizes order in which treatment tuples are assigned
    import random
    import copy
   # Adds extra treatment combinations in case things start to get unbalanced.
    if extras != None:
        for extra in extras: # assumes list of lists, e.g., [[True, C.FIRST_TREATMENT, False], [False, C.SECOND_TREATMENT, False]]
            data.append(extra)
    combos_to_reorder = copy.deepcopy(data)
    A = [a for a in combos_to_reorder]
    random.shuffle(A)
    return A








#=================================# 


