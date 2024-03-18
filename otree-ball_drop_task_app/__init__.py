from otree.api import *
# from common_functions import * # 

doc = """
    Developed by Faith Bague-Sampson, University of California, Irvine, 2022-2024.
    Bucket 01 is the TARGET bucket.
    Randomizes treatment between the dictator and rule-following tasks and the side on which the target bucket appears.
    This version employs a hard-timer, but it's optional. Just adjust the code.
"""


class C(BaseConstants):
# ~~~ Primary settings
    NAME_IN_URL = 'ball_drop_task'
    PLAYERS_PER_GROUP = None # there are no groups in this version. adjust if the dictator task uses other players
    NUM_BALLS = 15 # the total number of balls to allocate between the buckets
    NUM_ROUNDS = NUM_BALLS # the number of rounds is equal to the number of balls to be allocated
    STYLES_LOCAL = __name__ + '/zLocalStyles.html' # stylesheet that controls layout and styles of page content
# ~~~ Secondary settings
    DISPLAYED_SECTION_TITLE = "Part I" 
    MINUTES_FOR_TASK = 10 # hard timer -- in minutes
    DISPLAY_TIME_CUTOFF = 1.5 # in seconds
    STAMP_DIGITS = 4
 # ~~~ Payoffs
    PAYOFF_BUCKET_01 = 3 # payoff for each ball in cents (RF) # *** Bucket 01 is the TARGET bucket ***
    PAYOFF_BUCKET_02 = 6 # payoff for each ball in cents (RF)
    PAYOFF_DICTATOR = 9 # payoff for each ball in cents (D)
 # ~~~ Ball buckets
    COLOR_BUCKET_01 = 'blue' # in-text references to the color # *** Bucket 01 is the TARGET bucket ***
    COLOR_TITLE_01 = 'Blue' # the official label
    COLOR_BUCKET_02 = 'orange' # in-text references to the color
    COLOR_TITLE_02 = 'Orange' # the official label
    CHARITY_TITLE = 'The Charity' # placeholder name for the charity so the app works without a player first choosing a charity
    STYLE_BUCKET_01 = 'styleText_Bucket_01' # css class name assigned to references of the TARGET bucket # *** Bucket 01 is the TARGET bucket ***
    STYLE_BUCKET_02 = 'styleText_Bucket_02' # css class name assigned to references of the non-target bucket

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
# ~~~ Treatments/State/record-keeping
    task = models.BooleanField(
        choices=[[True, 'RF'], [False, 'D']],
        doc="""Treatment condition assigned to subject: TRUE = 1 = RF = Rule-Following Task, FALSE = 0 = D = Dictator Task.""",) # records assigned treatment condition
    bucket_01_on_left = models.BooleanField() # records / determines which side the blue charity/rule-following bucket is on, right or left (assigned); TRUE = B1 on left
    did_timeout_happen = models.BooleanField() # records if they timed out on the ball task (computed)
    time_stamp = models.FloatField() # records when they made their decision in the ball-task (computed)
    time_placed_in_bucket = models.StringField() # for each ball, records time elapsed since landing on the bucket drop page -- STRINGs!
# ~~~ Decisions during Ball Task
    bucket = models.StringField()
    bucket_01_clicks = models.IntegerField(initial=0) # Records a 1 if the ball is placed in bucket 01, otherwise 0 (chosen)
    bucket_02_clicks = models.IntegerField(initial=0) # Records a 1 if the ball is placed in bucket 02, otherwise 0(chosen)
# ~~~ Outcomes
    sum_bucket_01_clicks = models.IntegerField(min=0) # records the sum of bucket 01 drops for each participant (computed)
    sum_bucket_02_clicks = models.IntegerField(min=0) # records the sum of bucket 02 drops for each participant (computed)
    donation = models.CurrencyField(min=0) # records the value of the donation in every round (computed)
    total_donation = models.CurrencyField(min=0) # computes the cumulative total donated (computed)



# =========== FUNCTIONS =========== 

# ~~~ Originally imported from "common_functions app" ~~~ 
# randomize_order, set_expiration_time, get_time_from_start, addZero, make_it_base_sixty

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

def set_expiration_time(minutes_for_task): # sets the time at which X expires; expiry = set_expiration_time()
    import time
    expiry = time.time() + minutes_for_task*60
    return expiry

def get_time_from_start(minutes_for_task, expiry): # time elapsed since the start of the timer. # print(make_it_base_sixty(get_time_from_start(MINUTES_FOR_TASK, expiry),k))
    import time
    return minutes_for_task*60 - (expiry - time.time())

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



# ==== Tags players with their assigned treatment conditions from subsession 1 ==== 
def import_treatments(subsession: Subsession):
    for p in subsession.get_players():
        participant = p.participant
        treatments = participant.treatments
        p.task = treatments["task"]
        p.bucket_01_on_left = treatments["bucket_01_on_left"]

# ~~~ Assign treatments when subsessions are created
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        import itertools
    # all possible treatments
        treatments = itertools.cycle( itertools.product([True, False],[True, False]) )
    # generate balanced treatment group combinations
        treatment_combinations = []
        for t in range(1,5):
            treatment = next(treatments)
            treatment_combinations.append([treatment[0], treatment[1]])
    # generate random assignment order for treatments
        assignments = randomize_order(treatment_combinations, None)
    # assign treatments to subjects by order of arrival
        assignment = itertools.cycle(assignments)
        for p in subsession.get_players():
            participant = p.participant
            next_assignment = next(assignment)
            p.task = next_assignment[0] # nature of the ball task
            p.bucket_01_on_left = next_assignment[1] # side of Bucket_01
            participant.treatments = {'task': p.task, 'bucket_01_on_left': p.bucket_01_on_left} # record the treatment assignments to participant variables for access across apps
    # for each participant, records the other participants in their task treatment
        for player in subsession.get_players():
                participant = player.participant 
                participant.treatments["others_in_task"] = [w.participant.id_in_session for w in player.get_others_in_subsession() if w.task == player.participant.treatments["task"]] # == player.task
    else: # in every subsession, rewrite participant characteristics so that they're constant across rounds
        import_treatments(subsession)

# ~~~ Computes the number of balls that have been allocated to each bucket
def n_balls_in_bucket_01(player: Player):
    return sum(p.bucket_01_clicks for p in player.in_all_rounds())

def n_balls_in_bucket_02(player: Player):
    return sum(p.bucket_02_clicks for p in player.in_all_rounds())

# ~~~ Cumulative sum of balls placed into each bucket
def compute_balls_per_urn(player: Player):
    player.sum_bucket_01_clicks = n_balls_in_bucket_01(player)
    player.sum_bucket_02_clicks = n_balls_in_bucket_02(player)

# ~~~ Set participant payoffs for each so they get paid
def set_payoff(player: Player):
    if player.participant.treatments["task"] == False: # player.participant.treatments["task"] # player.task == False
        player.payoff = cu(player.bucket_02_clicks*C.PAYOFF_DICTATOR/100) # if player is dictator task, paid for balls placed in bucket_02 only
    else:
        player.payoff = cu(player.bucket_01_clicks*C.PAYOFF_BUCKET_01/100 + player.bucket_02_clicks*C.PAYOFF_BUCKET_02/100) # if player is rule-following task, payoff for balls placed into either bucket

# ~~~ Record player donations to charity
def set_donation(player: Player):
    if player.participant.treatments["task"] == False: # player.task == False:
        donation = cu((player.bucket_01_clicks*C.PAYOFF_DICTATOR)/100)
    else:
        donation = cu(0)
    return donation

# ~~~ Record total player donations to charity
def set_total_donation(player: Player):
    if player.participant.treatments["task"] == False: # player.task == False:
        other_allocations = n_balls_in_bucket_01(player)
        total_donation = cu(other_allocations*C.PAYOFF_DICTATOR/100)
    else:
        total_donation = cu(0)
    return total_donation

# ~~~ Record app results for posterity
def package_payoff_object(player: Player):
    player.participant.paid_rounds_object = {'payoff_ball_task': sum(p.payoff for p in player.in_all_rounds()),
                                             'bucket_01_allocations': n_balls_in_bucket_01(player),
                                             'bucket_02_allocations': n_balls_in_bucket_02(player),
                                             'charity': C.CHARITY_TITLE, 
                                             'donation': set_total_donation(player),}

# ~~~ Get hard-time remaining in ball-task
def get_timeout_seconds(player: Player):
    participant = player.participant
    import time
    return participant.expiry - time.time()

# ~~~ Records the bucket selected by participant
def set_bucket_selection(player: Player):
    if player.bucket == 'bucket_01':
        player.bucket_01_clicks = 1 # += 1
        player.bucket_02_clicks = 0 ## adjustments for server issues
    else:
        player.bucket_01_clicks = 0 ## adjustments for server issues
        player.bucket_02_clicks = 1 # += 1


# =========== PAGES =========== 

# ~~~ instructions for the ball task
class Instructions(Page): 
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    def before_next_page(player, timeout_happened):
        import time
        player.participant.expiry = set_expiration_time(C.MINUTES_FOR_TASK)
        player.time_stamp = time.time()

    def vars_for_template(player: Player):
        return dict(
            player_charity = 'The Charity',
            player_task = player.task,
        )

# ~~~ ball task page
class Ball_Task(Page):
    form_model = 'player'
    form_fields = ['bucket']
    get_timeout_seconds = get_timeout_seconds

    @staticmethod
    def is_displayed(player): 
        return get_timeout_seconds(player) > C.DISPLAY_TIME_CUTOFF # return player.round_number < C.NUM_ROUNDS + 1
    
    def js_vars(player: Player):
        bucket_01_num_balls = n_balls_in_bucket_01(player)
        bucket_02_num_balls = n_balls_in_bucket_02(player)
        return dict(
                round_number = player.round_number,
                bucket_01_num_balls = bucket_01_num_balls,
                bucket_02_num_balls = bucket_02_num_balls,
            )

    def before_next_page(player, timeout_happened):
        set_bucket_selection(player)
        set_payoff(player)
        compute_balls_per_urn(player)
        player.donation = set_donation(player)
        player.total_donation = set_total_donation(player)
        player.time_placed_in_bucket = make_it_base_sixty(get_time_from_start(C.MINUTES_FOR_TASK, player.participant.expiry), C.STAMP_DIGITS)
        player.time_stamp = round(get_timeout_seconds(player), 4)
        if timeout_happened == True:
            player.time_stamp = 0
            player.did_timeout_happen = True
        else:
            player.time_stamp = get_timeout_seconds(player)
            player.did_timeout_happen = False

    def vars_for_template(player: Player):
        bucket_01_allocations = n_balls_in_bucket_01(player)
        bucket_02_allocations = n_balls_in_bucket_02(player)
    # Dictates the information visible to the player on the buckets
        if player.participant.treatments["task"] == False: # player.task == False:
            bucket_01_title = C.CHARITY_TITLE
            bucket_02_title = 'You'
            bucket_01_payoff = bucket_01_allocations*C.PAYOFF_DICTATOR/100 
            bucket_02_payoff = bucket_02_allocations*C.PAYOFF_DICTATOR/100
            bucket_01_historyName = 'Charity\'s'
            bucket_02_historyName = 'Your'
        else:
            bucket_01_title = C.COLOR_TITLE_01
            bucket_02_title = C.COLOR_TITLE_02
            bucket_01_payoff = bucket_01_allocations*C.PAYOFF_BUCKET_01/100
            bucket_02_payoff = bucket_02_allocations*C.PAYOFF_BUCKET_02/100
            bucket_01_historyName = bucket_01_title
            bucket_02_historyName = bucket_02_title
    # Determines if Bucket_01 appears on the right or on the left
        if player.participant.treatments["bucket_01_on_left"] == True: # player.bucket_01_on_left == True: 
            bucket_01_float = 'style="float:left;"' 
            bucket_02_float = 'style="float:right;"' 
        else: 
            bucket_01_float = 'style="float:right;"' 
            bucket_02_float = 'style="float:left;"' 
    # Variables sent to template
        return dict (
            player_task = player.participant.treatments["task"],
            balls_remaining = C.NUM_BALLS - player.round_number + 1,
            bucket_01_payoff = bucket_01_payoff,
            bucket_02_payoff = bucket_02_payoff,
            player_earnings = bucket_01_payoff + bucket_02_payoff,
            total_balls = bucket_01_allocations + bucket_02_allocations, 
            bucket_01_allocations = bucket_01_allocations,
            bucket_02_allocations = bucket_02_allocations,
            bucket_01_title = bucket_01_title,
            bucket_02_title = bucket_02_title,
            bucket_01_historyName = bucket_01_historyName,
            bucket_02_historyName = bucket_02_historyName,
            bucket_01_float = bucket_01_float,
            bucket_02_float = bucket_02_float,
        )


# ~~~ payoff summary: provides task-specific payoffs 
class Task_Summary(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    def before_next_page(player, timeout_happened):
        package_payoff_object(player)

    def vars_for_template(player: Player):
        bucket_01_allocations = n_balls_in_bucket_01(player)
        bucket_02_allocations = n_balls_in_bucket_02(player)
        
        if player.task == False:
            player_task = 'Dictator'
            bucket_01_title = 'The Charity\'s'
            bucket_02_title = 'Your'
            bucket_01_payoff = bucket_01_allocations*C.PAYOFF_DICTATOR/100
            bucket_02_payoff = bucket_02_allocations*C.PAYOFF_DICTATOR/100
        else:
            player_task = 'Rule-Following'
            bucket_01_title = C.COLOR_TITLE_01
            bucket_02_title = C.COLOR_TITLE_02
            bucket_01_payoff = bucket_01_allocations*C.PAYOFF_BUCKET_01/100
            bucket_02_payoff = bucket_02_allocations*C.PAYOFF_BUCKET_02/100
        return dict(
            player_task = player_task,
            player_earnings = player.participant.payoff, 
            bucket_01_payoff = cu(bucket_01_payoff),
            bucket_02_payoff = cu(bucket_02_payoff),
            bucket_01_title = bucket_01_title,
            bucket_02_title = bucket_02_title,
            bucket_01_allocations = bucket_01_allocations,
            bucket_02_allocations = bucket_02_allocations,
        )




page_sequence = [Instructions, Ball_Task, Task_Summary]
