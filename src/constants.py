import pygtrie

# ADD PROMPTS
PROMPT_BRACKET = "What bracket is this opponent in? Optional field, will default to role bracket number."
PROMPT_OPP_NAME = "Enter the name of the opponent (CASE SENSITIVE)."
PROMPT_OPP_ONE = "Enter the opponent's first team in the order displayed in game. "
PROMPT_OPP_TWO = "Enter the opponent's second team in the order displayed in game."
PROMPT_OPP_THREE = "Enter the opponent's third team in the order displayed in game, or a question mark if unknown."
PROMPT_COUNTER_ONE = "Enter your first team in the order displayed in game."
PROMPT_COUNTER_TWO = "Enter your second team in the order displayed in game."
PROMPT_COUNTER_THREE = "Enter your third team in the order displayed in game, or a question mark if you won in 2."
PROMPT_BA_OPP = "Enter the opponent's team in the order displayed in game."
PROMPT_BA_COUNTER = "Enter the counter for the opponent's team."

# DESCRIPTIONS
DESC_ADD_PA = "Adds a new opponent's PA teams and their counters to your PA bracket or one that you specify."
DESC_ADD_BA = "Adds a BA comp and its counter."
DESC_GET_BA = "Gets counters for the specified BA comp."
DESC_COMMAND_EMBED = "Please type one of the following commands."
DESC_DONE = "done: Completes your /get_ba_counters command and cleans up the channel."
DESC_UPVOTE = "Upvotes the counter on the specified page."
DESC_DOWNVOTE = "Downvotes the counter on the specified page."
DESC_REMOVE_VOTE = "Removes your vote for the counter on the specified page."
DESC_REMOVE_COUNTER = "Removes the counter on the specified page."
DESC_ALIASES = "All supported aliases for units with multiple valid names (e.g. Lima/Rima). "

# UNIT AlIASES
ALIAS_KYARU = ['kyaru', 'karyl']
ALIAS_SKYARU = ['skyaru', 'skaryl', 'summerkyaru', 'summerkaryl']
ALIAS_STAMAKI = ['stamaki', 'summertamaki', 'stama']
ALIAS_HSHINOBU = ['hshinobu', 'halloweenshinobu']
ALIAS_LIMA = ['lima', 'rima']
ALIAS_VERIKO = ['veriko', 'valentineeriko']
ALIAS_KYOUKA = ['kyouka', 'kyoka']
ALIAS_NYREI = ['nyrei', 'newyearrei']
ALIAS_XAYANE = ['xayane', 'holidayayane', 'christmasayane']
ALIAS_PECORINE = ['pecorine', 'peco']
ALIAS_SUMMERPECORINE = ['specorine', 'speco', 'summerpeco', 'summerpecorine']
ALIAS_SKOKKORO = ['skokkoro', 'summerkokkoro', 'skoko', 'summerkoko']
ALIAS_MIYAKO = ['miyako', 'pudding']
ALIAS_HMIYAKO = ['hmiyako', 'halloweenmiyako', 'hpudding', 'halloweenpudding']
ALIAS_NYYUI = ['nyyui', 'newyearyui', 'newyearsyui', 'nyui']
ALIAS_VSHIZURU = ['vshizuru', 'vshizu', 'valentinesshizuru', 'valentineshizuru']
ALIAS_SSUZUME = ['ssuzume', 'summersuzume']
ALIAS_HIYORI = ['hiyori', 'hyori']
ALIAS_NYHIYORI = ['nyhiyori', 'nyhyori', 'newyearshiyori', 'newyearhyori']
ALIAS_XKURUMI = ['xkurumi', 'holidaykurumi', 'christmaskurumi']
ALIAS_SMIFUYU = ['smifuyu', 'summermifuyu']
ALIAS_XCHIKA = ['xchika', 'holidaychika', 'christmaschika']
ALIAS_HMISAKI = ['hmisaki', 'halloweenmisaki']
ALIAS_ILLYA = ['illya', 'ilya']
ALIAS_KUUKA = ['kuuka', 'kuka', 'kukka']
ALIAS_CHRISTINA = ['christina', 'chris']

ALIASES = [ALIAS_HIYORI,
           ALIAS_HMISAKI,
           ALIAS_HMIYAKO,
           ALIAS_HSHINOBU,
           ALIAS_ILLYA,
           ALIAS_KUUKA,
           ALIAS_KYARU,
           ALIAS_KYOUKA,
           ALIAS_LIMA,
           ALIAS_MIYAKO,
           ALIAS_NYHIYORI,
           ALIAS_NYREI,
           ALIAS_NYYUI,
           ALIAS_PECORINE,
           ALIAS_SKOKKORO,
           ALIAS_SKYARU,
           ALIAS_SMIFUYU,
           ALIAS_SSUZUME,
           ALIAS_STAMAKI,
           ALIAS_SUMMERPECORINE,
           ALIAS_VERIKO,
           ALIAS_VSHIZURU,
           ALIAS_XAYANE,
           ALIAS_XCHIKA,
           ALIAS_XKURUMI,
           ALIAS_CHRISTINA]


# LIST OF ALL OTHER CHARACTERS
REMAINING_CHARACTERS = ['yui', 'rei', 'shizuru', 'rino', 'nozomi', 'chika', 'tsumugi', 'mimi', 'misato', 'aoi',
                        'shinobu',
                        'yori', 'akari', 'jun', 'tomo', 'matsuri', 'saren', 'suzume', 'ayane', 'kurumi',
                        'maho', 'makoto', 'kaori', 'kasumi', 'mahiru', 'rin', 'shiori', 'akino', 'yukari', 'mifuyu',
                        'tamaki', 'anna', 'ruka', 'eriko', 'nanaka', 'mitsuki', 'io', 'suzuna', 'misaki', 'monika',
                        'ninon', 'yuki', 'ayumi', 'chieru', 'chloe', 'djeeta', 'arisa', 'luna', 'grea', 'anne',
                        'lou', 'emilia', 'rem', 'ram', 'muimi', 'neneka', ' karin', 'hatsune']


def trie_setup():
    t = pygtrie.CharTrie()
    for alias_list in ALIASES:
        for char_name in alias_list:
            t[char_name] = alias_list[0]
    for char_name in REMAINING_CHARACTERS:
        t[char_name] = char_name

    return t


# TRIE
TRIE = trie_setup()

# OTHER GLOBALS


DELETE_DELAY = 3
DICT_COMMAND_EMBED = command_embed_dict = {
    'title': "List of commands",
    'description': DESC_COMMAND_EMBED,
    'fields': [
        {
            'name': 'done',
            'value': DESC_DONE,
        },
        {
            'name': 'upvote <page #>',
            'value': DESC_UPVOTE
        },
        {
            'name': 'downvote <page #>',
            'value': DESC_DOWNVOTE
        },
        {
            'name': 'removevote <page #>',
            'value': DESC_REMOVE_VOTE
        },
        {
            'name': 'removecounter <page #>',
            'value': DESC_REMOVE_COUNTER
        }]
}
