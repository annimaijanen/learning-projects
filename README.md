# learning-projects

Repository for learning and experimenting with LLM applications.

## Streamlit Game Recommendation Bot

This Streamlit app is a small game recommendation chatbot.
It recommends new games for the user based on their preferences.
Available here: https://games-recommender-bot.streamlit.app/

### Logic

1. The user selects preferences using hard filters
   (language, genre, platform, price category, release year, etc.)
2. The bot analyzes the filtered games and asks two clarifying questions.
3. Based on the user's answers, the bot recommends a matching game.

### Technology

- Streamlit
- Python
- pandas
- OpenAI GPT-4o

The application uses Steam game metadata and "About the game" descriptions
to match games with the user's preferences.

## Steam Games Metacritic Analysis

Exploratory analysis and clustering on Steam games with Metacritic scores.

### Topics

- Statistics of Metacritic categories
  (mean price, release year, amount of games, etc.)
- Clustering to explore game types
- PCA for visualization

### Technology

- Python
- pandas
- matplotlib
- scikit-learn
