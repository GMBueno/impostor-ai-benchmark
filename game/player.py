import random
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

from config import SYSTEM_PROMPT

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

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

                    voted_player = next((p for p in players if p.name == voted_for_name), None)

                    if voted_player and voted_player != self:
                        print(f"{self.name} votes for {voted_player.name}")
                        return voted_player
                    else:
                        print(f"{self.name} made an invalid vote for '{voted_for_name}'. Choosing a random player.")
                else:
                    print(f"Model {self.model} returned an empty response. Retrying...")
                    time.sleep(2)
            except Exception as e:
                print(f"Error calling model {self.model}: {e}. Retrying...")
                time.sleep(2)

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
        return "word" 