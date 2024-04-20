
pokemon_statements = [
    ("Pikachu evolves into Raichu by using a Thunder Stone.", True),
    ("The Pokémon Bulbasaur is a Grass/Poison-type.", True),
    ("Charmander is a Water-type Pokémon.", False),
    ("Mew is a Mythical Pokémon.", True),
    ("Ash Ketchum is the main protagonist in the Pokémon anime series.", "True"),
    ("The move 'Splash' deals damage to the opponent.", False),
    ("Dragonite is known as the Dragon Pokémon.", True),
    ("Jigglypuff's song can put its audience to sleep.", True),
    ("Meowth is a member of Team Rocket.", True),
    ("Gyarados evolves from Magikarp.", True),
    ("Eevee can evolve into seven different Pokémon.", False),
    ("Charizard is a Fire/Flying-type Pokémon.", True),
    ("Pikachu's pre-evolution is Pichu.", False),
    ("Mewtwo is the result of genetic experiments.", True),
    ("Snorlax is known for its high speed.", False),
    ("The Pokémon Ditto can transform into any other Pokémon.", True),
    ("Gengar is weak against Psychic-type moves.", True),
    ("The Legendary Pokémon Articuno is a Fire-type.", False),
    ("Machop evolves into Machoke, which then evolves into Machamp.", True),
    ("The Pokémon Eevee has only one evolution form.", False)
]

import random

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Player:
    '''Internal GameManager class to help keep track of each player seperately.'''
    def __init__(self, id, name, num):
        self._id = id
        self._player_num = num
        self._name = name
        self._disqualified = False
        self._score = 0
        self._has_answered_this_round = False

    
    def get_id(self):
        return self._id
    
    def get_name(self):
        return self._name
    
    def get_player_num(self):
        return self._player_num
    
    def get_score(self):
        return self._score
       
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

    def prep_to_next_round(self):
        self._has_answered_this_round = False

    

class GameManager:
    def __init__(self):
        self._players = dict()
        self._active_players_ids = list()
        self._round = 1
        self._player_num = 1
        self._statements = pokemon_statements.copy()
        self._total_rounds = len(self._statements)
        self._this_round_statement = None
        self._game_active = True
    
    def game_active(self):
        return self._game_active

    def add_player(self, id, name):
        self._players[id] = Player(id, name, self._player_num)
        self._active_players_ids.append(id)
        self._player_num += 1
    
    def deactivate_player(self, id):
        self._active_players_ids.remove(id)

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

        ret = bcolors.OKCYAN + "Round " + str(self._round) +":" +bcolors.ENDC + "\n"
        for id in self._active_players_ids:
            self._players[id].prep_to_next_round()
            ret += "Player " + str(self._players[id].get_player_num()) + ": " + self._players[id].get_name() + "\n"
        return ret + bcolors.OKCYAN + "=======" + bcolors.ENDC + "\n"
    
    def choose_question(self):
        '''The function chooses and returns this round statement as a string formatted: 

            "
            True or False: (This round's statement)\n
            "
        '''
        random.shuffle(self._statements)

        self._this_round_statement = self._statements.pop()
        return bcolors.UNDERLINE + "True or False:" + bcolors.ENDC + " " + bcolors.BOLD + self._this_round_statement[0] + bcolors.ENDC + '\n'
    
    def gather_answer(self, id, answer):
        '''The function gathers an answer from each player, and verifies it.'''
        if id in self._active_players_ids:
            if answer == self._this_round_statement[1]:
                self._players[id].correct_answer()
                return
            self._players[id].disqualify()

    def sum_round(self):
        '''The function readies the game for the next round.'''

        self._round += 1

        #if all the questions are done
        if (self._round > self._total_rounds):
            remaining_players = list(map(lambda active_player: active_player.get_name(), filter(lambda player: player.get_id() in self._active_players_ids, self._players.values())))
            self._game_active = False
            return bcolors.OKGREEN + f"No more questions!\n {remaining_players} are the winners!" + bcolors.ENDC + "\n"
        else:
            #disqualifying those who did not answer this round
            for id in self._active_players_ids:
                if not self._players[id].has_answered_this_round():
                    self._players[id].disqualify()

            #check if all disqualified
            move_on_round_flag = True
            for id in self._active_players_ids:
                if not self._players[id].is_disqualified():
                    move_on_round_flag = False
                    break

            #if all the active players is disqualified this round, undisqualify them and move on the next round as is
            if move_on_round_flag:
                for id in self._active_players_ids:
                    self._players[id].undisqualify()
                return bcolors.FAIL + "All the players didn't know the answer. Moving on to the next round!" + bcolors.ENDC + "\n"
            
            # else deactivate the disqualified players
            else:
                ret = ""
                disqualified_this_round = []
                for id in self._active_players_ids:
                    if self._players[id].is_disqualified():
                        disqualified_this_round.append(id)
                        ret += bcolors.FAIL + self._players[id].get_name() + " is incorrect!" + bcolors.ENDC + "\n"
                    else:
                        ret += bcolors.OKGREEN + self._players[id].get_name() + " is correct!"+ bcolors.ENDC + "\n"
                
                if len(disqualified_this_round) != len(self._active_players_ids):
                    for id in disqualified_this_round:
                        self.deactivate_player(id)

                if len(self._active_players_ids) == 1:
                    ret += bcolors.UNDERLINE + bcolors.OKCYAN + self._players[self._active_players_ids[0]].get_name() + " Wins!" +bcolors.ENDC + "\n"
                    self._game_active = False   
                return ret + '\n'

    def sum_game(self):
        '''For bonus purposes, returning list of tuples (player_name, player_score) of this game'''
        return list(map(lambda player: (player.get_name(), player.get_score()), self._players.values()))
        
        