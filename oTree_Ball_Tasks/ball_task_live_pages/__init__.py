from otree.api import *
from shared_functions import * # randomize_order, set_expiration_time, get_time_from_start, addZero, make_it_base_sixty, record_json_obj, recall_json_obj

doc = """
    Developed by Faith Bague-Sampson, University of California, Irvine, 2022-2024.
    basic ball task with LIVE pages: 
    * several of the participant variables are now models.LongStringField()
    * using json, decisions are appeneded to lists that are stored as strings
    
    Note: several variables have what will no doubt be considered annoyingly different names than those found in the "basic" version. 
    Fijate bien, mon ami.
    
    Randomizes treatment between the dictator and rule-following tasks and the side on which the target bucket appears.
    Bucket 01 is the TARGET bucket.
    * Rule-Following task when player.task == True
    * Dictator task when player.task == False
    * Target bucket is on the left-hand side of the screen when player.bucket_01_on_left == True
    * Target bucket is on the right-hand side of the screen when player.bucket_01_on_left == False
    
    To use a hard-timer, set C.TASK_IS_TIMED = True. 
    By default, the features and information presented on the Ball_Task.html template is controlled by this setting. 
    
    By default, the number of balls to place into buckets determines the number of rounds to be played.
    App relies on local css stylesheet, a global stylesheet, 1 .js scripts, and imported python functions.

"""


class C(BaseConstants):
# ~~~ Primary settings
    NAME_IN_URL = 'ball_drop_task_live'
    PLAYERS_PER_GROUP = None # default: app does not use groups. adjust if the dictator task uses other players
    NUM_BALLS = 10 # the total number of balls to allocate between the buckets
    NUM_ROUNDS = 1 # default: number of balls determines number of rounds
    TASK_IS_TIMED = True # if use a hard-timer = True; if no timer = False
# ~~~ Secondary (time) settings 
    # default: these constants required even if TASK_IS_TIMED = False
    TIME_FOR_TASK = 2 # length of time to complete ball task (hard timer)
    TIMED_IN_MINUTES = True # units for TIME_FOR_TASK: minutes = True; seconds = False
    DISPLAY_TIME_CUTOFF = 1.5 # measured in seconds
    STAMP_DIGITS = 4 # see the function "make_it_base_sixty(..., STAMP_DIGITS)" for usage
 # ~~~ Payoffs
    PAYOFF_BUCKET_01 = 3 # payoff for each ball in cents (RF) # *** Bucket 01 is the TARGET bucket ***
    PAYOFF_BUCKET_02 = 6 # payoff for each ball in cents (RF)
    PAYOFF_DICTATOR = 9 # payoff for each ball in cents (D)
 # ~~~ Ball bucket in-text references
    COLOR_BUCKET_01 = 'blue' # in-text references to Bucket_01's color # *** Bucket 01 is the TARGET bucket ***
    COLOR_TITLE_01 = 'Blue' # the official label  # *** Bucket 01 is the TARGET bucket ***
    COLOR_BUCKET_02 = 'orange' # in-text references to Bucket_02's color
    COLOR_TITLE_02 = 'Orange' # the official label
    CHARITY_TITLE = 'The Charity' # placeholder for the participants' charity selection; adjust according to your selection process # *** TARGET bucket in dictator games***
# ~~~ General styles and display
    STYLES_LOCAL = __name__ + '/zLocalStyles.html' # local stylesheet -- most styles are required
    DISPLAYED_SECTION_TITLE = "Part I" # optional
    STYLE_BUCKET_01 = 'styleText_Bucket_01' # css class for text refs to bucket_01 # *** Bucket 01 is the TARGET bucket ***
    STYLE_BUCKET_02 = 'styleText_Bucket_02' # css class for text refs to bucket_02, the non-target bucket
      

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
    did_timeout_happen = models.BooleanField(default=False) # records if they timed out on the ball task (computed)
    time_stamp = models.LongStringField() # records when they made their decision in the ball-task (computed)
    time_placed_in_bucket = models.LongStringField() # for each ball, records time elapsed since landing on the bucket drop page -- STRINGs!
# ~~~ Decisions during Ball Task
    bucket = models.StringField(choices=[['bucket_01', 'bucket_01'], ['bucket_02', 'bucket_02']])
    chose_bucket_01 = models.LongStringField() # allows experimenter to track decisions as they are made even with live pages: Records a 1 if the ball is placed in bucket 01, otherwise 0.
# ~~~ Outcomes
    total_donation = models.CurrencyField(initial=0, min=0) # computes the cumulative total donated (computed)
    num_balls_dropped = models.IntegerField(initial=0, min=0, max=C.NUM_BALLS)
    sum_drops_bucket_01 = models.IntegerField(initial=0, min=0) # records the sum of bucket 01 drops for each participant (computed)
    sum_drops_bucket_02 = models.IntegerField(initial=0, min=0) # records the sum of bucket 02 drops for each participant (computed)


# =========== FUNCTIONS =========== #

# ==== Tags players with their assigned treatment conditions from subsession 1 ==== #
def import_treatments(subsession: Subsession):
    for p in subsession.get_players():
        participant = p.participant
        treatments = participant.treatments
        p.task = treatments["task"]
        p.bucket_01_on_left = treatments["bucket_01_on_left"]

# ~~~ Assign treatments when subsessions are created ~~~
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        import itertools
    # all possible treatments  
        if subsession.session.config['treatment_condition'] == 0:
            treatments = itertools.cycle( itertools.product([False], [True, False]) )
            n = 3
        elif subsession.session.config['treatment_condition'] == 1:
            treatments = itertools.cycle( itertools.product([True], [True, False]) )
            n = 3
        else:
            treatments = itertools.cycle( itertools.product([True, False], [True, False]) )
            n = 5
    # generate balanced treatment group combinations
        treatment_combinations = []
        for t in range(1,n):
            treatment = next(treatments)
            treatment_combinations.append([treatment[0], treatment[1]])
    # generate random assignment order for treatments
        assignments = randomize_order(treatment_combinations, None)
    # assign treatments to subjects by order of arrival
        assignment = itertools.cycle(assignments)
        for p in subsession.get_players():
            next_assignment = next(assignment)
            p.task = next_assignment[0] # nature of the ball task
            p.bucket_01_on_left = next_assignment[1] # side of Bucket_01
            p.participant.treatments = {'task': p.task, 'bucket_01_on_left': p.bucket_01_on_left} # record the treatment assignments to participant variables for access across apps
    # initialize the list variables; allows experimenter to track decisions as they are made even with live pages
            p.chose_bucket_01 = record_json_obj([]) # creates an empty list (as a string object)
            p.time_placed_in_bucket = record_json_obj([])
            p.time_stamp = record_json_obj([])
    # for each participant, records the other participants in their task treatment
        for player in subsession.get_players():
                player.participant.treatments["others_in_task"] = [w.participant.id_in_session for w in player.get_others_in_subsession() if w.task == player.participant.treatments["task"]] # == player.task
   
    else: # in every subsession, rewrite participant characteristics so that they're constant across rounds
        import_treatments(subsession)

# ~~~ Returns the name of the charity conditional on treatment condition ~~~
def set_charity_name(player: Player):
    if player.participant.treatments["task"] == False:
        charity_name = C.CHARITY_TITLE
    else:
        charity_name = 'NA'
    return charity_name

# ~~~ Record app results for posterity ~~~
def package_payoff_object(player: Player):
    player.participant.paid_rounds_object = {'payoff_ball_task': player.payoff,
                                             'bucket_01_allocations': player.sum_drops_bucket_01,
                                             'bucket_02_allocations': player.sum_drops_bucket_02,
                                             'charity': set_charity_name(player), 
                                             'donation': player.total_donation,}

# ~~~ Get hard-time remaining in ball-task ~~~
def get_timeout_seconds(player: Player):
    import time
    return player.participant.expiry - time.time()

# ~~~ Grab data for templates; reduces redundancies ... maybe ~~~
def get_page_vars(player: Player):
    if player.participant.treatments["task"] == False:
        target_title = set_charity_name(player)
        non_target_history_title = 'Your'
        return dict(
            target_title = target_title,
            target_possessive = target_title + '\'s',
            target_history_title = target_title.strip('The ') + '\'s',
            non_target_title = 'You',
            non_target_possessive = non_target_history_title + 's',
            non_target_history_title = non_target_history_title,
        )
    else:
        target_title = C.COLOR_TITLE_01
        non_target_title = C.COLOR_TITLE_02
        return dict(
            target_title = target_title,
            target_possessive = target_title,
            target_history_title = target_title,
            non_target_title = non_target_title,
            non_target_possessive = non_target_title,
            non_target_history_title = non_target_title,
        )

def summarise_current_state(player: Player):
    return dict(
        balls_remaining = max(C.NUM_BALLS - player.num_balls_dropped, 0),
        balls_in_bucket01 = player.sum_drops_bucket_01,
        balls_in_bucket02 = player.sum_drops_bucket_02,
        bucket_01_payoffs = sum_earned_bucket_01(player),
        bucket_02_payoffs = sum_earned_bucket_02(player),
        totalEarnings = player.payoff,
        puedeSeguir = continue_task(player),
    )

# ~~~ Determines if the task continues ~~~
def continue_task(player: Player):
    if player.num_balls_dropped >= C.NUM_BALLS:
        return False
    else:
        return True

# ~~~ Capture or compute individual decisions and their outcomes ~~~
def set_payoff_bucket_01(player: Player):
    if player.participant.treatments["task"] == False:
        return 0 
    else:
        return C.PAYOFF_BUCKET_01/100 
    
def set_payoff_bucket_02(player: Player):
    if player.participant.treatments["task"] == False:
        return C.PAYOFF_DICTATOR/100 
    else:
        return C.PAYOFF_BUCKET_02/100
    
def set_donation(player: Player):
    if player.participant.treatments["task"] == False: # player.task == False:
        return C.PAYOFF_DICTATOR/100
    else:
        return 0

# ~~~ Handle json string conversions for LongStringField variables ~~~
def set_bucket_order(player: Player, b01):
    bucket_order = recall_json_obj(player.chose_bucket_01, False)
    bucket_order.append(b01)
    player.chose_bucket_01 = record_json_obj(bucket_order)

def record_event_time(player: Player):
    if C.TASK_IS_TIMED == True:
        placed = make_it_base_sixty(get_time_from_start(C.TIME_FOR_TASK, player.participant.expiry, C.TIMED_IN_MINUTES), C.STAMP_DIGITS)
        stamped = round(get_timeout_seconds(player), 4)
    else:
        placed = make_it_base_sixty(abs(get_timeout_seconds(player)), C.STAMP_DIGITS)
        stamped = abs(round(get_timeout_seconds(player), 4))
    time_placed = recall_json_obj(player.time_placed_in_bucket, False)
    time_placed.append(placed)
    player.time_placed_in_bucket = record_json_obj(time_placed)
    time_stamp = recall_json_obj(player.time_stamp, False)
    time_stamp.append(stamped)
    player.time_stamp = record_json_obj(time_stamp)

# ~~~ Compute the total payoffs attributable to each bucket ~~~
def sum_earned_bucket_01(player: Player):
    if player.participant.treatments["task"] == False:
        return player.sum_drops_bucket_01*set_donation(player)
    else:
        return player.sum_drops_bucket_01*set_payoff_bucket_01(player)

def sum_earned_bucket_02(player: Player):
    return player.sum_drops_bucket_02*set_payoff_bucket_02(player)

# ~~~ Records consequence of ball allocation ~~~
def selection_consequence(player: Player):
    if player.bucket == 'bucket_01' or player.bucket == 'bucket_02':
        if player.bucket == 'bucket_01':
            player.sum_drops_bucket_01 += 1
            player.payoff += set_payoff_bucket_01(player)
            player.total_donation += set_donation(player)
            set_bucket_order(player, 1)
        else:
            player.sum_drops_bucket_02 += 1
            player.payoff += set_payoff_bucket_02(player)
            set_bucket_order(player, 0)
        player.num_balls_dropped += 1
        record_event_time(player)
    if continue_task(player) == True:
        player.bucket = None



# =========== PAGES =========== #

# ~~~ instructions for the ball task  ~~~
class Instructions(Page): 
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    def before_next_page(player, timeout_happened):
        import time
        if C.TASK_IS_TIMED == True: 
            player.participant.expiry = round(set_expiration_time(C.TIME_FOR_TASK, C.TIMED_IN_MINUTES), 4)
        else:
            player.participant.expiry = time.time()
            
    def vars_for_template(player: Player):
        if C.TIMED_IN_MINUTES == False: 
            time_units = 'seconds'
        elif C.TIME_FOR_TASK == 1:
            time_units = 'minute'
        else:
            time_units = 'minutes'
        return dict(
            player_charity = set_charity_name(player), 
            player_task = player.task,
            time_units = time_units,
        )


# ~~~ ball task ~~~
class Ball_Task(Page):
    form_model = 'player'
    form_fields = ['bucket']
    if C.TASK_IS_TIMED == True:
        get_timeout_seconds = get_timeout_seconds

    @staticmethod
    def is_displayed(player: Player): 
        if C.TASK_IS_TIMED == True:
            return get_timeout_seconds(player) > C.DISPLAY_TIME_CUTOFF and continue_task(player)
        else:
            return continue_task(player)
    
    def js_vars(player: Player):
        player_info = summarise_current_state(player)
        return dict(
            balls_remaining = player_info["balls_remaining"],
            balls_in_bucket01 = player_info["balls_in_bucket01"],
            balls_in_bucket02 = player_info["balls_in_bucket02"],
            bucket_01_payoffs = player_info["bucket_01_payoffs"],
            bucket_02_payoffs = player_info["bucket_02_payoffs"],
            totalEarnings = player_info["totalEarnings"],
            )
        
    def live_method(player: Player, pageData):
        player.bucket = pageData
        selection_consequence(player)
        player_info = summarise_current_state(player)
        return {player.id_in_group: player_info}
        
    def before_next_page(player, timeout_happened): 
        if C.TASK_IS_TIMED == True and timeout_happened == True:
            player.did_timeout_happen = True
            record_event_time(player)
        else:
            player.did_timeout_happen = False

    def vars_for_template(player: Player): 
    # Dictates the information visible to the player
        page_vars = get_page_vars(player)
        if C.TASK_IS_TIMED == True:
            row_two_contents = 'ball_bag_with_tables.html'
        else:
            row_two_contents = 'ball_bag_simple.html'
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
            bucket_01_title = page_vars["target_title"],
            bucket_02_title = page_vars["non_target_title"],
            bucket_01_historyName = page_vars["target_history_title"],
            bucket_02_historyName = page_vars["non_target_history_title"],
            bucket_01_float = bucket_01_float,
            bucket_02_float = bucket_02_float,
            row_two_contents = row_two_contents,
        )


# ~~~ payoff summary: provides task-specific payoffs ~~~
class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    def before_next_page(player, timeout_happened):
        package_payoff_object(player)

    def vars_for_template(player: Player):
        page_vars = get_page_vars(player)
        player_info = summarise_current_state(player)        
        if player.task == False:
            player_task = 'Dictator'
        else:
            player_task = 'Rule-Following'
        return dict(
            player_task = player_task,
            player_earnings = player.participant.payoff, 
            bucket_01_payoff = cu(player_info["bucket_01_payoffs"]),
            bucket_02_payoff = cu(player_info["bucket_02_payoffs"]),
            bucket_01_title = page_vars["target_possessive"],
            bucket_02_title = page_vars["non_target_possessive"],
            bucket_01_allocations = player_info["balls_in_bucket01"],
            bucket_02_allocations = player_info["balls_in_bucket02"],
            total_balls = player_info["balls_in_bucket01"] + player_info["balls_in_bucket02"],
        )



page_sequence = [Instructions, Ball_Task, Results]

