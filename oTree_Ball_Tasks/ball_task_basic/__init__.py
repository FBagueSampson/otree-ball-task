from otree.api import *
from shared_functions import * # randomize_order, set_expiration_time, get_time_from_start, addZero, make_it_base_sixty

doc = """
    Developed by Faith Bague-Sampson, University of California, Irvine, 2022-2024.
    
    Randomizes treatment between the dictator and rule-following tasks and the side on which the target bucket appears.
    Bucket 01 is the TARGET bucket.
    * Rule-Following task when player.task == True
    * Dictator task when player.task == False
    * Target bucket is on the left-hand side of the screen when player.bucket_01_on_left == True
    * Target bucket is on the right-hand side of the screen when player.bucket_01_on_left == False
    
    To use a hard-timer, set C.TASK_IS_TIMED = True. 
    By default, the features and information presented on the Ball_Task.html template is controlled by this setting. 
    
    By default, the number of balls to place into buckets determines the number of rounds to be played.
    App relies on local css stylesheet, a global stylesheet, 3 .js scripts, and imported python functions.

"""


class C(BaseConstants):
# ~~~ Primary settings
    NAME_IN_URL = 'ball_drop_task'
    PLAYERS_PER_GROUP = None # default: app does not use groups. adjust if the dictator task uses other players
    NUM_BALLS = 10 # the total number of balls to allocate between the buckets
    NUM_ROUNDS = NUM_BALLS # default: number of balls determines number of rounds
    TASK_IS_TIMED = True # if use a hard-timer = True; if no timer = False
# ~~~ Secondary (time) settings
    # default: these constants required even if TASK_IS_TIMED = False
    TIME_FOR_TASK = 1 # length of time to complete ball task (hard timer)
    TIMED_IN_MINUTES = True # units for TIME_FOR_TASK: minutes = True; seconds = False
    DISPLAY_TIME_CUTOFF = 1.5 # measured in seconds
    STAMP_DIGITS = 3 # see the function "make_it_base_sixty(..., STAMP_DIGITS)" for usage
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



# =========== FUNCTIONS =========== #

# ==== Tags players with their assigned treatment conditions from subsession 1 ==== #
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

# ~~~ Returns the name of the charity conditional on treatment condition  ##########***************************************
def set_charity_name(player: Player):
    if player.participant.treatments["task"] == False:
        charity_name = C.CHARITY_TITLE
    else:
        charity_name = 'NA'
    return charity_name


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
    return sum(p.donation for p in player.in_all_rounds())


# ~~~ Record app results for posterity
def package_payoff_object(player: Player):
    player.participant.paid_rounds_object = {'payoff_ball_task': sum(p.payoff for p in player.in_all_rounds()),
                                             'bucket_01_allocations': n_balls_in_bucket_01(player),
                                             'bucket_02_allocations': n_balls_in_bucket_02(player),
                                             'charity': set_charity_name(player), 
                                             'donation': set_total_donation(player),}

# ~~~ Get hard-time remaining in ball-task
def get_timeout_seconds(player: Player):
    import time
    return player.participant.expiry - time.time()

# ~~~ Records the bucket selected by participant
def set_bucket_selection(player: Player, timeout_happened):
    if timeout_happened == True:
        player.bucket = None
        player.bucket_01_clicks = 0
        player.bucket_02_clicks = 0
    else:
        if player.bucket == 'bucket_01':
            player.bucket_01_clicks = 1 # += 1
            player.bucket_02_clicks = 0 ## adjustments for server issues
        else:
            player.bucket_01_clicks = 0 ## adjustments for server issues
            player.bucket_02_clicks = 1 # += 1


def get_page_vars(player: Player):  ##########***************************************
    if player.participant.treatments["task"] == False:
        target_title = set_charity_name(player)
        non_target_possessive = 'Your'
        return dict(
            target_title = target_title,
            target_possessive = target_title + '\'s',
            target_history_title = target_title.strip('The ') + '\'s',
            non_target_title = 'You',
            non_target_possessive = 'Your',
            non_target_history_title = non_target_possessive,
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



# ~~~ Computes the total payoffs attributable to each bucket
def sum_bucket_01_payoff(player: Player):  ##########***************************************
    if player.participant.treatments["task"] == False:
        return 0 
    else:
        return n_balls_in_bucket_01(player)*C.PAYOFF_BUCKET_01/100 

def sum_bucket_02_payoff(player: Player):  ##########***************************************
    if player.participant.treatments["task"] == False:
        return n_balls_in_bucket_02(player)*C.PAYOFF_DICTATOR/100 
    else:
        return n_balls_in_bucket_02(player)*C.PAYOFF_BUCKET_02/100 


# =========== PAGES =========== #

# ~~~ instructions for the ball task
class Instructions(Page): 
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    def before_next_page(player, timeout_happened):
        import time
        player.time_stamp = time.time()
        if C.TASK_IS_TIMED == True: 
            player.participant.expiry = set_expiration_time(C.TIME_FOR_TASK, C.TIMED_IN_MINUTES)
        else:
            player.participant.expiry = player.time_stamp

    def vars_for_template(player: Player):
        if C.TIMED_IN_MINUTES == False: 
            time_units = 'seconds'
        elif C.TIME_FOR_TASK == 1:
            time_units = 'minute'
        else:
            time_units = 'minutes'
            
        return dict(
            player_charity = 'The Charity',
            player_task = player.task,
            time_units = time_units,
        )


class Ball_Task(Page):
    form_model = 'player'
    form_fields = ['bucket']
    if C.TASK_IS_TIMED == True:
        get_timeout_seconds = get_timeout_seconds

    @staticmethod
    def is_displayed(player): 
        if C.TASK_IS_TIMED == True:
            return get_timeout_seconds(player) > C.DISPLAY_TIME_CUTOFF
        else:
            return player.round_number < C.NUM_ROUNDS + 1
    
    def js_vars(player: Player):
        bucket_01_num_balls = n_balls_in_bucket_01(player)
        bucket_02_num_balls = n_balls_in_bucket_02(player)
        return dict(
                round_number = player.round_number,
                bucket_01_num_balls = bucket_01_num_balls,
                bucket_02_num_balls = bucket_02_num_balls,
            )

    def before_next_page(player, timeout_happened):
        set_bucket_selection(player, timeout_happened)
        set_payoff(player)
        compute_balls_per_urn(player)
        player.donation = set_donation(player)
        player.total_donation = set_total_donation(player)
        if C.TASK_IS_TIMED == True:
            player.time_placed_in_bucket = make_it_base_sixty(get_time_from_start(C.TIME_FOR_TASK, player.participant.expiry, C.TIMED_IN_MINUTES), C.STAMP_DIGITS)
            player.time_stamp = round(get_timeout_seconds(player), 4)
            if timeout_happened == True:
                player.time_stamp = 0
                player.did_timeout_happen = True
        else:
            player.time_placed_in_bucket = make_it_base_sixty(abs(get_timeout_seconds(player)), C.STAMP_DIGITS)
            player.time_stamp = round(get_timeout_seconds(player), 4)
            player.did_timeout_happen = False


    def vars_for_template(player: Player):
        bucket_01_allocations = n_balls_in_bucket_01(player)
        bucket_02_allocations = n_balls_in_bucket_02(player)
        bucket_01_payoff = sum_bucket_01_payoff(player)
        bucket_02_payoff = sum_bucket_02_payoff(player)
    # Dictates the information visible to the player on the buckets
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
            balls_remaining = C.NUM_BALLS - player.round_number + 1,
            bucket_01_payoff = bucket_01_payoff,
            bucket_02_payoff = bucket_02_payoff,
            player_earnings = bucket_01_payoff + bucket_02_payoff,
            total_balls = bucket_01_allocations + bucket_02_allocations, 
            bucket_01_allocations = bucket_01_allocations,
            bucket_02_allocations = bucket_02_allocations,
            bucket_01_title = page_vars["target_title"],
            bucket_02_title = page_vars["non_target_title"],
            bucket_01_historyName = page_vars["target_history_title"],
            bucket_02_historyName = page_vars["non_target_history_title"],
            bucket_01_float = bucket_01_float,
            bucket_02_float = bucket_02_float,
            row_two_contents = row_two_contents,
        )


# ~~~ payoff summary: provides task-specific payoffs 
class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    
    def before_next_page(player, timeout_happened):
        package_payoff_object(player)

    def vars_for_template(player: Player):
        page_vars = get_page_vars(player)
        bucket_01_allocations = n_balls_in_bucket_01(player)
        bucket_02_allocations = n_balls_in_bucket_02(player)
        bucket_01_payoff = sum_bucket_01_payoff(player)
        bucket_02_payoff = sum_bucket_02_payoff(player)
        if player.task == False:
            player_task = 'Dictator'
        else:
            player_task = 'Rule-Following'
        return dict(
            player_task = player_task,
            player_earnings = player.participant.payoff, 
            bucket_01_payoff = cu(bucket_01_payoff),
            bucket_02_payoff = cu(bucket_02_payoff),
            bucket_01_title = page_vars["target_title"],
            bucket_02_title = page_vars["non_target_title"],
            bucket_01_allocations = bucket_01_allocations,
            bucket_02_allocations = bucket_02_allocations,
            total_balls = bucket_01_allocations + bucket_02_allocations,
        )




page_sequence = [Instructions, Ball_Task, Results]
