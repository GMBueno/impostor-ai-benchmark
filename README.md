# Impostor AI Benchmark

This project introduces a novel benchmark for evaluating the reasoning, strategic, and deceptive capabilities of large language models (LLMs) through a social deduction game called "Impostor" (based on "Undercover").

## Why This Benchmark?

Traditional NLP benchmarks (like GLUE or SuperGLUE) are excellent for measuring a model's linguistic capabilities, but they often fall short in assessing more nuanced, human-like skills such as strategic thinking, theory of mind, and deception.

The Impostor AI Benchmark places multiple AI agents in a competitive, multi-round game where they must use natural language to achieve their objectives. This dynamic environment serves as a testbed to evaluate how well models can:
- Generate contextually relevant and strategic language.
- Deduce hidden information from the inputs of others.
- Adapt their strategy based on evolving game states.
- Deceive other players when in the role of the "impostor".

## How The Game Works

The game is simple, yet allows for complex strategies to emerge.

1.  **Setup**: The game begins with 5 players. Four are randomly assigned the role of "Civilian" and one is the "Impostor".
2.  **The Secret Word**: The four civilians are given a secret word, chosen randomly from a predefined list. The impostor does not know this word.
3.  **Rounds**:
    - Each player takes a turn to say a single word that should be related to the secret word.
    - Civilians aim to give clues that are clear enough for other civilians but subtle enough to not reveal the secret word to the impostor.
    - The impostor, having no knowledge of the word, must use the civilians' words as clues to say something that blends in.
4.  **Voting**: After every player has said a word, a voting phase begins. All players vote to eliminate who they suspect is the impostor.
5.  **Elimination & Win Conditions**:
    - If a **Civilian** is voted out, the game continues to the next round with the remaining players.
    - If the **Impostor** is voted out, they have one final chance to guess the secret word. If they guess correctly, the Impostor wins. If not, the Civilians win.
    - If the Impostor survives until only one other player remains, the **Impostor** wins.

## The Scoring System: A Path to Ranking Models

This game is designed to be run thousands of times to generate a robust performance score for each AI model. By tracking wins and losses across a large number of games, we can quantify a model's skill.

A simple scoring system is proposed:
- **Civilian Win**: 1 points
- **Civilian Loss**: 0 points
- **Impostor Win**: 5 points
- **Impostor Loss**: 0 points

By running simulations at scale, we can generate a leaderboard that ranks models not just on their language proficiency, but on their ability to strategize, reason, and "play" a game effectively.

\~\~\~ vibe coded \~\~\~

## Getting Started

### Prerequisites

- Python 3.12
- An API key from [OpenRouter.ai](https://openrouter.ai/) to access the various models.

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/GMBueno/impostor-ai-benchmark.git
    cd impostor-ai-benchmark
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your API key:**
    Create a file named `.env` in the root of the project and add your OpenRouter API key:
    ```
    OPENROUTER_API_KEY="your-openrouter-key-here"
    ```

5.  **Run the game:**
    ```bash
    python3 main.py
    ```

## Limitations & Future Work

This benchmark is still in its early stages and has several limitations:

- **Limited Word List**: The pool of secret words is currently small, which can lead to repetitive games.
- **Fixed Models**: The models are hard-coded. A more flexible system would allow for easier integration of new models.
- **Simple Scoring**: The scoring is straightforward but could be enhanced to reward more nuanced behaviors (e.g., identifying the impostor early).

We encourage contributions to address these limitations! Future work could include:
- Expanding the word list significantly.
- Creating a framework to easily add and evaluate new LLMs.
- Developing a more sophisticated scoring and analytics suite.
- Building a web-based interface to visualize the games and results.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make your changes, and submit a pull request. You can contribute by adding new words, suggesting models, improving the game logic, or enhancing the documentation.
