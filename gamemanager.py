
pokemon_statements = [
    ("Pikachu evolves into Raichu by using a Thunder Stone.", "True"),
    ("The Pokémon Bulbasaur is a Grass/Poison-type.", "True"),
    ("Charmander is a Water-type Pokémon.", "False"),
    ("Mew is a Mythical Pokémon.", "True"),
    ("Ash Ketchum is the main protagonist in the Pokémon anime series.", "True"),
    ("The move 'Splash' deals damage to the opponent.", "False"),
    ("Dragonite is known as the Dragon Pokémon.", "True"),
    ("Jigglypuff's song can put its audience to sleep.", "True"),
    ("Meowth is a member of Team Rocket.", "True"),
    ("Gyarados evolves from Magikarp.", "True"),
    ("Eevee can evolve into seven different Pokémon.", "False"),
    ("Charizard is a Fire/Flying-type Pokémon.", "True"),
    ("Pikachu's pre-evolution is Pichu.", "False"),
    ("Mewtwo is the result of genetic experiments.", "True"),
    ("Snorlax is known for its high speed.", "False"),
    ("The Pokémon Ditto can transform into any other Pokémon.", "True"),
    ("Gengar is weak against Psychic-type moves.", "True"),
    ("The Legendary Pokémon Articuno is a Fire-type.", "False"),
    ("Machop evolves into Machoke, which then evolves into Machamp.", "True"),
    ("The Pokémon Eevee has only one evolution form.", "False")
]

import random
import functools

class Player:
    '''Internal GameManager class to help keep track of each player seperately.'''
    def __init__(self, id, name, num):
        self._id = id
        self._player_num = num
        self._name = name
        self._disqualified = False
        self._score = 0
        self._is_active = True
        self._has_answered_this_round = False

    
    def get_id(self):
        return self._id
    
    def get_name(self):
        return self._name
    
    def get_player_num(self):
        return self._player_num
    
    def is_active(self):
        return self._is_active
    
    def is_disqualified(self):
        return self._disqualified
    
    def has_answered_this_round(self):
        return self._has_answered_this_round

    def correct_answer(self):
        self._score += 1
        self._has_answered_this_round = True
    
    def disqualify(self):
        self._disqualified = True
        self._has_answered_this_round = True

    def undisqualify(self):
        self._disqualified = False

    def deactivate(self):
        self._is_active = False

    def prep_to_next_round(self):
        self._has_answered_this_round = False

    

    
    


class GameManager:
    def __init__(self):
        self._players = dict()
        self._round = 1
        self._player_num = 1
        self._statements = pokemon_statements
        self._this_round_statement = None
    
    def add_player(self, id, name):
        self._players[id] = Player(id, name, self._player_num)
        self._player_num += 1
    
    def round_init(self):
        '''The function check for remaining player and returns pre-round string of the remaining players:

            "
            Player 1: Name
            Player 2: Name \n
            .\n
            .\n
            Player n: Name\n
            ====\n
            "
        '''
        ret = "Round " + str(self._round) +":\n"
        for player in self._players.values():
            if player.is_active():
                ret += "Player " + str(player.get_player_num()) + ": " + player.get_name() + "\n"
        return ret + "====\n"

    
    def choose_question(self):
        '''The function chooses and returns this round statement as a string formatted: 

            "
            True or False: (This round's statement)\n
            "
        '''
        random.shuffle(self._statements)
        self._this_round_statement = self._statements.pop()
        return "True or False: " + self._this_round_statement[0]
    
    def gather_answer(self, id, answer):
        '''The function gathers an answer from each player, and verifies it. returns True if player was right otherwise False'''
        if answer == self._this_round_statement[1]:
            self._players[id].correct_answer()
            return True
        self._players[id].disqualify()
        return False

    def sum_round(self):
        '''The function readies the game for the next round.'''
        #gather active players
        active_players = filter(lambda player: player.is_active(), self._players.values())

        #disqualifying those who did not answer
        map(lambda not_answered_player: not_answered_player.disqualify(), filter(lambda active_player: not active_player.has_answered_this_round(), active_players))

        #if all the players answered wrong or did not answer, move on. else deactivate those who were wrong or did not answer in the given time.
        if all(map(lambda active_players: active_players.is_disqualified(), active_players)):
            map(lambda active_player: active_player.undisqualify(), active_players)
        else:
            map(lambda player: player.deactivate() ,filter(lambda active_player: active_player.is_disqualified(), active_players))
            
        #prepare next round
        map(lambda player: player.prep_to_next_round(), self._players.values())    
        self._round += 1