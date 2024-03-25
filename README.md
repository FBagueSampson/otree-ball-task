# otree-ball-task
An oTree project with two click-and-drag, ball-drop apps, a live-pages version and a basic version.

The apps are designed to be used as an interface for dictator games, rule-following tasks, or a mix of both tasks randomly assigned at the start of the session.

In each treatment, participants are provided with a number of balls that they can drag into one of two buckets using their mouse, the target bucket or the alternative bucket. 

App Features:
* One adjustment to the session-config settings sets the mode: dictator, rule-following, balanced-random-assignment of the two tasks
* Includes optional hard-timer (records if a timeout happened)
* The bucket colors and ball sizes are easily adjustable (no find and replace, just adjust the desired variable in one location)
* Automatically captures other participants assigned to the same task
* Automatically records a time stamp of when a ball is placed into a bucket
* Automatic balanced-random-assignment of the order in which the target and alternative buckets appear

In the rule-following task, participants are told that the rule is to place the ball into the target bucket. Typical of such tasks, balls placed into the target bucket earn less than balls placed in the alternative bucket.

In the dictator task, participants are told to allocate the balls between the buckets where the amount earned by balls dropped into the "target" bucket is donated to a charity (this can be customized to be another participant or bot), and the amount earned by placing balls into the alternative bucket accrue as a payoff to the participant.

Ball Task Features:
* Buckets highlight when balls are dragged over them
* To place a ball, participants drag the ball over the bucket then release their mouse
* Only balls placed within buckets are counted
* There is a brief animation of the ball falling into the bucket when participants release the ball
* Placed balls accumulate in the buckets with each ball placed


NOTE:
Ball Task Apps are dependent on the following items not contained within the individual app folders:
* global css
* global javascript files
* functions imported from the shared_functions app
* PARTICIPANT_FIELDS and SESSION_CONFIGS settings in the settings.py file


![ball-drop task set up for dictator game; includes a hard timer](https://github.com/FBagueSampson/otree-ball-task/blob/main/charity_ball_task_001.png?raw=true)


