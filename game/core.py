import random
import time

from config import MODELS
from game.player import Player

def load_words(file_path='words.txt'):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Warning: '{file_path}' not found. Using default word list.")
        return ["internet", "Greece", "jacket", "netflix", "coca-cola", "star", "watch", "violin"]

class ImpostorGame:
    def __init__(self, num_players=5):
        self.players = [Player(f"Player {i+1}", MODELS[i]) for i in range(num_players)]
        self.word_list = load_words()
        self.secret_word = ""
        self.impostor = None
        self.civilians = []
        self.round_words = {}
        self.game_over = False
        self.winner = None
        self.history = []
        self.round_number = 1

    def setup_game(self):
        print("--- Setting up a new game of Impostor ---")
        self.secret_word = random.choice(self.word_list)
        
        impostor_index = random.randint(0, len(self.players) - 1)
        
        self.civilians = []
        for i, player in enumerate(self.players):
            if i == impostor_index:
                player.set_role('impostor')
                self.impostor = player
            else:
                player.set_role('civilian')
                self.civilians.append(player)
        
        print(f"The secret word has been chosen.")
        print(f"There are {len(self.civilians)} civilians and 1 impostor.")
        print(f"The impostor is: {self.impostor.name} (for debugging purposes)")
        print(f"The secret word is: {self.secret_word} (for debugging purposes)")
        print("-" * 20)

    def play_round(self):
        self.round_words = {}
        print(f"\n--- Starting Round {self.round_number} ---")
        
        start_player_index = random.randint(0, len(self.players) - 1)
        print(f"{self.players[start_player_index].name} will start this round.")
        
        player_order = self.players[start_player_index:] + self.players[:start_player_index]

        context = []
        for player in player_order:
            if player.role == 'civilian':
                word = player.get_word(self.history, context, self.secret_word)
            else:  # Impostor
                word = player.get_word(self.history, context)
            context.append(word)
            self.round_words[player.name] = word
            time.sleep(0.5)
        
        self.history.append(self.round_words)

    def voting_phase(self):
        print("\n--- Voting Phase ---")
        votes = {}
        
        voting_context = [f"{p.name} said '{p.word_said}'" for p in self.players]

        for player in self.players:
            voted_for = player.vote(self.players, self.history, voting_context)
            if voted_for:
                votes[voted_for.name] = votes.get(voted_for.name, 0) + 1
        
        print("\n--- Voting Results ---")
        for name, count in votes.items():
            print(f"{name}: {count} vote(s)")

        if not votes:
            print("No votes were cast. This round is a draw.")
            return

        max_votes = max(votes.values())
        eliminated_players = [name for name, count in votes.items() if count == max_votes]

        if len(eliminated_players) > 1:
            print("\nThere is a tie in the vote. No one is eliminated. Starting a new round.")
            self.round_number += 1
            return

        eliminated_player_name = eliminated_players[0]
        eliminated_player = next(p for p in self.players if p.name == eliminated_player_name)
        
        print(f"\n{eliminated_player.name} has been eliminated with {max_votes} votes.")

        if eliminated_player.role == 'impostor':
            print("The eliminated player was the IMPOSTOR!")
            self.impostor_guess_phase()
        else:
            print("The eliminated player was a CIVILIAN. The game continues.")
            self.players.remove(eliminated_player)
            self.civilians.remove(eliminated_player)
            self.round_number += 1

    def impostor_guess_phase(self):
        print(f"\n--- Impostor's Final Guess ---")
        print(f"{self.impostor.name}, you have one chance to guess the secret word.")
        
        guess = self.impostor.guess_secret_word(self.history)
        print(f"{self.impostor.name} ({self.impostor.model}) guesses the word is: '{guess}'")

        if guess.lower() == self.secret_word.lower() or guess.lower() in self.secret_word.lower() or self.secret_word.lower() in guess.lower():
            print(f"Correct! The secret word was '{self.secret_word}'.")
            self.winner = "Impostor"
        else:
            print(f"Incorrect! The secret word was '{self.secret_word}'.")
            self.winner = "Civilians"
        
        self.game_over = True

    def check_win_conditions(self):
        if len(self.players) - len(self.civilians) > len(self.civilians) or len(self.civilians) < 1:
             self.winner = "Impostor"
             self.game_over = True


    def run_game(self):
        self.setup_game()
        while not self.game_over:
            self.play_round()
            self.voting_phase()
            if not self.game_over:
                self.check_win_conditions()
        
        print(f"\n--- Game Over ---")
        print(f"The winner is: {self.winner}!") 