PLUGINS = [
    # Built-ins
    "niko.plugins.admin",
    "niko.plugins.friendly",
    "niko.plugins.web",

    # All plugins in your project.
    "plugins",
]



CHAT_CLIENT = 'skype' # Only skype is impltemented at this time

DATABASE_FILE = 'niko.db'

SCHEDULERS = {
    'yesterdaysMood' : '09:45',
    'reminder' : '17:00'
}

MOODS = {
    'very good' : {
        'score' : 2,
        'smileys' : [':d'],
        'messages' : [
            'Hei, sunshine! The database did a little dance recording this entry.',
            'That good, huh? Please tell us your secrets'
        ]
    },
    'good' : {
        'score' : 1,
        'smileys' : [':)'],
        'messages' : [
            'You\'re a jolly fellow, aren\'t you?!',
            'Looks like you did something fun today. Keep up the good work!'
        ]
    },
    'neutral' : {
        'score' : 0,
        'smileys' : [':|'],
        'messages' : [
            'Alright, entry stored. Carry on with your meh self.',
            'Meh, chould have been worse. Keep your chin up.'
        ]
    },
    'bad' : {
        'score' : -1,
        'smileys' : [':(', '(sad)'],
        'messages' : [
            'Sorry that things aren\'t going well! Go find a pick-me-up.',
            'Today is not a good day for science.'
        ]
    },
    'very bad' : {
        'score' : -2,
        'smileys' : [':\'(', '(cry)'],
        'messages' : [
            'Oh no! Please go find a sympathetic ear. Or a hug.',
            'That\'s a darn shame. Maybe tomorrow thing will take a turn for the best.'
        ]
    }
}