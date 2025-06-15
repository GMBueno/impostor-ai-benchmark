import random
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

SYSTEM_PROMPT = """
You are a player in a competitive social deduction game called Undercover. Your goal is to win and earn points.

**Game Rules & How to Win:**
- There are 5 players. 4 are 'civilians' and 1 is an 'impostor'.
- You will be assigned a role (civilian or impostor) and a player name.

**If you are a Civilian:**
- You will receive a secret word. All civilians receive the same word.
- **Your Goal:** Identify and vote out the impostor.
- **How you win:** The civilians win if the impostor is voted out and fails to guess the secret word. You get +10 points for winning.
- **How you lose:** You lose if the impostor wins. You get -5 points for losing.
- **Strategy:** When it's your turn to speak, say a single word related to the secret word. Your word should be a good clue for your fellow civilians, but not so obvious that the impostor can easily figure out the secret word. If your word is too unrelated, you might be suspected of being the impostor!

**If you are the Impostor:**
- You will NOT receive the secret word.
- **Your Goal:** Blend in with the civilians, avoid being voted out, and try to deduce the secret word.
- **How you win:** You win in two ways:
    1. If you are voted out, you get one final chance to guess the secret word. If you guess it correctly, you win.
    2. If you survive until only one other player is left.
- You get +25 points for winning.
- **How you lose:** You lose if you are voted out and guess the word incorrectly. You get -10 points for losing.
- **Strategy:** Listen carefully to the words the other players say. When it's your turn, say a single word that seems to fit the pattern. Your goal is to trick the civilians into thinking you know the secret word.

**Game Flow:**
1. The game proceeds in rounds.
2. In each round, each player says one word.
3. After everyone has spoken, all players vote to eliminate one player.
4. If a civilian is eliminated, the game continues to the next round with the remaining players.
5. The game ends when the impostor is eliminated or when only two players remain.

**Your Task:**
- When asked for a word, respond with only that single word.
- When asked to vote, respond with only the player's name (e.g., "Player 3").
"""

WORD_LIST = ["internet", "greece", "jacket"]
MODELS = [
    "google/gemini-2.5-flash-preview-05-20",
    "x-ai/grok-3-mini-beta",
    "openai/o4-mini-2025-04-16",
    "anthropic/claude-4-sonnet-20250522",
    "deepseek/deepseek-r1-0528",
]

class Player:
    def __init__(self, name, model, is_ai=True):
        self.name = name
        self.model = model
        self.is_ai = is_ai
        self.role = None
        self.word_said = None

    def set_role(self, role):
        self.role = role

    def get_word(self, game_history, context, secret_word=None):
        """
        Calls the OpenRouter API to get a word from the AI.
        """
        print(f"{self.name}'s turn to speak.")
        time.sleep(1)

        history_str = "Game History:\n"
        if not game_history:
            history_str += "No previous rounds.\n"
        for i, round_data in enumerate(game_history):
            history_str += f"--- Round {i+1} ---\n"
            words_str = ", ".join([f"{p}: '{w}'" for p, w in round_data.items()])
            history_str += f"Words said: {words_str}\n"

        prompt = f"You are {self.name}. You are the {self.role}.\n\n"
        prompt += history_str
        prompt += f"\n--- Current Round ---\n"
        prompt += f"Previous words in this round: {', '.join(context) if context else 'You are the first to speak.'}. "
        
        if self.role == 'civilian':
            prompt += f"Your secret word is '{secret_word}'. Say a related word."
        else:  # Impostor
            prompt += "You don't know the secret word. Say a word that fits with the others."

        for _ in range(3):  # 3 retries
            try:
                completion = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ]
                )
                if completion.choices:
                    chosen_word = completion.choices[0].message.content.strip().split()[0]
                    print(f"{self.name} ({self.model}) says: {chosen_word}")
                    self.word_said = chosen_word
                    return chosen_word
                else:
                    print(f"Model {self.model} returned an empty response. Retrying...")
                    time.sleep(2)
            except Exception as e:
                print(f"Error calling model {self.model}: {e}. Retrying...")
                time.sleep(2)

        print(f"Failed to get word from {self.name} after retries. Using a default word.")
        chosen_word = "pass"
        self.word_said = chosen_word
        return chosen_word

    def vote(self, players, game_history, context):
        """
        Calls the OpenRouter API to get a vote from the AI.
        """
        player_names = [p.name for p in players if p != self]

        history_str = "Game History:\n"
        if not game_history:
            history_str += "No previous rounds.\n"
        for i, round_data in enumerate(game_history):
            history_str += f"--- Round {i+1} ---\n"
            words_str = ", ".join([f"{p}: '{w}'" for p, w in round_data.items()])
            history_str += f"Words said: {words_str}\n"

        prompt = f"You are {self.name}. You are the {self.role}.\n\n"
        prompt += history_str
        prompt += "\n--- Current Round Voting ---\n"
        prompt += f"Here are the words said in the round: {', '.join(context)}. \n"
        prompt += f"The players still in the game are: {', '.join(player_names)}. \n"
        prompt += "Based on all the information, who do you vote to eliminate? Respond with the player name only."

        for _ in range(3):  # 3 retries
            try:
                completion = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ]
                )
                if completion.choices:
                    voted_for_name = completion.choices[0].message.content.strip()

                    # Find the player object from the name
                    voted_player = next((p for p in players if p.name == voted_for_name), None)

                    if voted_player and voted_player != self:
                        print(f"{self.name} votes for {voted_player.name}")
                        return voted_player
                    else:
                        # Handle cases where the model hallucinates a player name or votes for itself
                        print(f"{self.name} made an invalid vote for '{voted_for_name}'. Choosing a random player.")
                else:
                    print(f"Model {self.model} returned an empty response. Retrying...")
                    time.sleep(2)
            except Exception as e:
                print(f"Error calling model {self.model}: {e}. Retrying...")
                time.sleep(2)

        # Fallback to random vote if API fails or returns invalid response
        possible_targets = [p for p in players if p != self]
        target = random.choice(possible_targets)
        print(f"{self.name} votes for {target.name} (randomly)")
        return target

    def guess_secret_word(self, game_history):
        """
        Calls the OpenRouter API for the impostor to guess the secret word.
        """
        history_str = "Game History:\n"
        for i, round_data in enumerate(game_history):
            history_str += f"--- Round {i+1} ---\n"
            words_str = ", ".join([f"{p}: '{w}'" for p, w in round_data.items()])
            history_str += f"Words said: {words_str}\n"

        prompt = (
            "You are the impostor and you have been voted out.\n"
            "This is your last chance to win. You must guess the secret word.\n"
            "Here is the history of all the words said in the game:\n"
            f"{history_str}\n"
            "Based on this history, what do you think the secret word is? Respond with a single word."
        )

        for _ in range(3):  # 3 retries
            try:
                completion = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ]
                )
                if completion.choices:
                    guess = completion.choices[0].message.content.strip().split()[0]
                    return guess
                else:
                    print(f"Model {self.model} returned an empty response. Retrying...")
                    time.sleep(2)
            except Exception as e:
                print(f"Error calling model {self.model}: {e}. Retrying...")
                time.sleep(2)

        print("Failed to get guess from impostor after retries. Using a random word.")
        return random.choice(WORD_LIST)

class UndercoverGame:
    def __init__(self, num_players=5):
        self.players = [Player(f"Player {i+1}", MODELS[i]) for i in range(num_players)]
        self.secret_word = ""
        self.impostor = None
        self.civilians = []
        self.round_words = {}
        self.game_over = False
        self.winner = None
        self.history = []
        self.round_number = 1

    def setup_game(self):
        print("--- Setting up a new game of Undercover ---")
        self.secret_word = random.choice(WORD_LIST)
        
        impostor_index = random.randint(0, len(self.players) - 1)
        
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
            else: # Impostor
                word = player.get_word(self.history, context)
            context.append(word)
            self.round_words[player.name] = word
            time.sleep(0.5)
        
        self.history.append(self.round_words)

    def voting_phase(self):
        print("\n--- Voting Phase ---")
        votes = {}
        
        # Create context for voting
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

        # Mocking the impostor's guess
        guess = self.impostor.guess_secret_word(self.history)
        print(f"{self.impostor.name} ({self.impostor.model}) guesses the word is: '{guess}'")

        if guess.lower() == self.secret_word.lower():
            print(f"Correct! The secret word was '{self.secret_word}'.")
            self.winner = "Impostor"
        else:
            print(f"Incorrect! The secret word was '{self.secret_word}'.")
            self.winner = "Civilians"
        
        self.game_over = True

    def check_win_conditions(self):
        if len(self.civilians) <= 1:
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

if __name__ == "__main__":
    game = UndercoverGame()
    game.run_game()
