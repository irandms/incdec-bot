ROTATE_MAX_CHARS = 15

SUBGROUPS = {'EE': ['DiddleDad', 'fgsrfug', 'Selfishshellfish', 'aaronschraner'],
             'CS': ['tolvstaa', 'Codification', 'codysseus'],
             'CH': ['TheChemE'],
             'BO': ['adny_bot'],
             'AN': ['adny_bot', 'TheChemE', 'tolvstaa'],
             'CO': ['Codification', 'codysseys'],
             'GR': ['tolvstaa', 'Codification'],
             'NE': ['irandms'],
             'AL': []}

for users in SUBGROUPS.values():
    SUBGROUPS['AL'] += users

SUBGROUPS['AL'] = list(set(SUBGROUPS['AL']))
SUBGROUPS['EV'] = SUBGROUPS['AL']
