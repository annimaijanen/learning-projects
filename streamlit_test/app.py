import pandas as pd
from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from pathlib import Path

# Start by reading the data (games_recommender_clean.csv)
DATA_PATH = Path(__file__).parent / "games_recommender_clean.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

st.set_page_config(page_title="Streamlit Chat", page_icon="💬")

col1, col2 = st.columns([6, 2])
with col2:
    st.image("assets/gamer_bot.png", width=150)

with col1:
    st.title("Games Recommender")
    st.caption("Your friendly bot for finding what to play next.")

# Initialize session state variable to track setup completion
# Change these as needed
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "games_text" not in st.session_state:
    st.session_state.games_text = ""
if "filtered_games" not in st.session_state:
    st.session_state.filtered_games = pd.DataFrame()
if "questions_generated" not in st.session_state:
    st.session_state.questions_generated = False
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# Helper function to update session state
def complete_setup():
    st.session_state.setup_complete = True
def show_feedback():
    st.session_state.feedback_shown = True


# Setup stage for collecting user game preferences
if not st.session_state.setup_complete:
    
    st.subheader("Game preferences", divider = "rainbow")

    # Next implement the session state variables and hard filters

    # Here insert the hard filters for 
    # "required_age" -> user sets maximum age. all ages ok by default
    # "Supported languages" -> user can choose multiple, only one has to match. english by default
    # "Mac", "Linux", "Windows" = "System" -> user chooses one. all chosen by default.
    # "metacritic_category" -> user can choose multiple. all chosen by default.
    # "Genres" -> user can choose multiple. all chosen by default.
    # "price_category" -> user can choose multiple. all chosen by default.
    # "release_year" -> user can choose multiple, should be a range. all chosen by default.

    # --- Helper lists ---
    all_metacritic = sorted(df["metacritic_category"].dropna().unique())
    all_prices = sorted(df["price_category"].dropna().unique())
    genre_counts = (
        df["Genres"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
    )

    all_genres = genre_counts.head(15).index.tolist()

    # Implement the filters
    min_year = int(df["release_year"].min())
    max_year = int(df["release_year"].max())

    # --- Required age ---
    max_age = st.number_input(
        "Maximum required age",
        min_value=0,
        max_value=21,
        value=21,
        width = 300
    )

    # --- Supported languages ---

    all_languages = sorted(
        set(
            lang
            for langs in df["language_support"]
            .dropna()
            .apply(eval)
            for lang in langs
            if lang != "unknown"
        )
    )

    selected_languages = st.multiselect(
        "Supported languages",
        options=all_languages,
        default=["English"]
        )

    # --- System ---
    selected_systems = st.multiselect(
        "System",
        options=["Windows", "Mac", "Linux"],
        default=["Windows", "Mac", "Linux"]
    )

    # --- Metacritic ---
    selected_metacritic = st.multiselect(
        "Metacritic category",
        options=all_metacritic,
        default=all_metacritic
    )

    # --- Genres ---
    selected_genres = st.multiselect(
        "Genres",
        options=all_genres,
        default=all_genres
    )

    # --- Price ---
    selected_prices = st.multiselect(
        "Price category",
        options=all_prices,
        default=all_prices
    )

    # --- Release year ---
    selected_year_range = st.slider(
        "Release year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    # Implement the filtering

    filtered_df = df.copy()

    filtered_df = filtered_df[filtered_df["required_age"] <= max_age]

    filtered_df = filtered_df[
        filtered_df["language_support"].apply(
            lambda langs: any(lang in eval(langs) for lang in selected_languages)
        )
    ]

    filtered_df = filtered_df[
        filtered_df[selected_systems].any(axis=1)
    ]

    filtered_df = filtered_df[
        filtered_df["metacritic_category"].isin(selected_metacritic)
    ]

    filtered_df = filtered_df[
        filtered_df["price_category"].isin(selected_prices)
    ]

    filtered_df = filtered_df[
        filtered_df["Genres"].apply(
            lambda x: any(cat in str(x) for cat in selected_genres)
        )
    ]

    filtered_df = filtered_df[
        filtered_df["release_year"].between(
            selected_year_range[0],
            selected_year_range[1]
        )
    ]

    # Sanity Check
    # st.write(f"Games matching your filters: **{len(filtered_df)}**")

    # if len(filtered_df) > 0:
    #     top_20_preview = (
    #         filtered_df
    #         .sort_values("estimated_owners", ascending=False)
    #         .head(20)
    #     )

    #     with st.expander("Preview 20 most popular matching games"):
    #         st.dataframe(
    #             top_20_preview[[
    #                 "name",
    #                 "estimated_owners",
    #                 "Genres",
    #                 "price_category",
    #                 "metacritic_category",
    #                 "release_year"
    #             ]],
    #             width='stretch',
    #             hide_index=True
    #         )
    # else:
    #     st.warning("No games match your current filters.")

    # Games to send to LLM
    # 10 most popular
    top_games = (
        filtered_df
        .sort_values("estimated_owners", ascending=False)
        .head(10)
    )

    games_for_llm = top_games[[
    "name",
    "Genres",
    "About the game"
    ]].copy()

    # Shorten description
    games_for_llm["About the game"] = (
        games_for_llm["About the game"]
        .astype(str)
        .str.slice(0, 200)
    )

    games_text = games_for_llm.to_string(index=False)

        # Change this into a button to complete the part with hard filters
        # And start the LLM to ask some additional questions based on the user replies and the data that is left
        # Here we might use the "About the game" part

        # A button to complete the setup stage and ask an additional question

    if st.button("Game preferences set"):
        st.session_state.filtered_games = top_games
        st.session_state.games_text = games_text
        st.session_state.setup_complete = True
        st.write("Preferences complete. Asking for more details...")

# Recommendation chat stage
if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info(
        """
        I'll ask two quick questions to help find the best games for you.
        """,
        icon="🎮"
    )

    # Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    # The first bot will generate 2 new questions that will filter the data even more.
    # The questions should be based on the data that is left.

    # Check if messages is still an empty list (empty list -> false) #########
    if not st.session_state.messages:
        st.session_state.messages = [{
        "role": "system",
        "content": f"""
    You are a friendly game recommendation assistant.

    Here are 20 candidate games:
    {st.session_state.games_text}

    Ask one short preference question at a time.
    Ask only 2 questions total.
    Do not recommend games yet.
    """
        }]

    # Display messages
    for message in st.session_state.messages:
        if message["role"] != "system":

            avatar = None

            if message["role"] == "assistant":
                avatar = "assets/gamer_bot.png"

            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    # Generate assistant question if needed
    if st.session_state.question_count < 2 and (
        len(st.session_state.messages) == 1 or st.session_state.messages[-1]["role"] == "user"
    ):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages,
            stream=False,
        )

        response = stream.choices[0].message.content

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        st.session_state.question_count += 1
        st.rerun()

    # User answer
    if st.session_state.question_count <= 2:
        if prompt := st.chat_input("Your answer.", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})

            if st.session_state.question_count == 2:
                st.session_state.chat_complete = True

            st.rerun()

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get recommendation", on_click=show_feedback):
        st.write("Generating a recommendation...")

# Show feedback screen
if st.session_state.feedback_shown:
    st.subheader("Recommended games")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    # Initialize new OpenAI client instance for the game recommendations
    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Generate the recommended game using the stored messages and write a system prompt for the recommendation

    # The second bot will choose a game based on the information given to the first bot (extra info).

# The prompt needs to be rewritten
    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a helpful tool that selects the best matching game from the list, based on the answers of the two questions asked.
             Follow this format:
             Recommendation: Name of your recommended game.
             Description: About the game - information.
             Give only the recommendation and description and do not ask additional questions.
              """},
            {"role": "user", "content": f"These are the two questions and the answers. Keep in mind that you are only a tool. And you shouldn't engage in any converstation: {conversation_history}"}
        ]
    )

    st.write(feedback_completion.choices[0].message.content)

    # Button to restart the recommender
    if st.button("Restart Recommendation Bot", type="primary"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
