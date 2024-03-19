from os import environ

SESSION_CONFIGS = [
    dict(
        name='basic_ball_task', 
        app_sequence=['ball_task_basic'], 
        num_demo_participants=8,
        treatment_condition = 0, # takes values: dictator task = 0, rule-following task = 1, balanced treatment of both D and RF = 2
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=10.00, doc=""
)

PARTICIPANT_FIELDS = ['expiry', 'paid_rounds_object', 'treatments']
SESSION_FIELDS = []

DEBUG = 1

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ Let\'s play [oTree] ball [games]! """

SECRET_KEY = '9455566945902'
