# otree-ball-task
A flexible ball drop task app in oTree that can be used in dictator games or as a rule-following task.

The example has 4 treatments, so recommend num_demo_participants=4 so you can see the difference.

(Optionally) add the following three fields to the participant field list in your settings.py file. If not, you'll need to adjust the code some.
PARTICIPANT_FIELDS = ['expiry', 'paid_rounds_object', 'treatments']


