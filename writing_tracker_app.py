import streamlit as st
import pandas as pd
import datetime
import time
import threading
import os

# Ensure necessary dependencies are installed
try:
    import nltk
    from nltk.corpus import wordnet
except ModuleNotFoundError:
    os.system("pip install nltk")
    import nltk
    from nltk.corpus import wordnet

# Initialize session state
if 'writing_data' not in st.session_state:
    st.session_state.writing_data = []
if 'alarms' not in st.session_state:
    st.session_state.alarms = []
if 'calendar_events' not in st.session_state:
    st.session_state.calendar_events = []
if 'writing_text' not in st.session_state:
    st.session_state.writing_text = ""

# App title
st.title("Writing Progress Tracker")

# Sidebar for input
st.sidebar.header("Log Your Writing")

date = st.sidebar.date_input("Select Date", datetime.date.today())

# Add a text area for writing
writing_text = st.text_area(
    "Write Here:", 
    value=st.session_state.writing_text, 
    height=300,
    placeholder="Start writing here..."
)

# Update session state when writing text is changed
if writing_text != st.session_state.writing_text:
    st.session_state.writing_text = writing_text

# Calculate writing statistics
words_written = len(writing_text.split())
sentences_written = writing_text.count('.') + writing_text.count('!') + writing_text.count('?')
pages_written = words_written / 250  # Assuming 250 words per page
paragraphs_written = writing_text.count('\n')
time_spent = st.sidebar.number_input("Time Spent Writing (Minutes)", min_value=0, value=0, step=5)
nouns = st.sidebar.number_input("Nouns Used", min_value=0, value=0, step=1)
nouns_edited = st.sidebar.number_input("Nouns Improved", min_value=0, value=0, step=1)
verbs = st.sidebar.number_input("Verbs Used", min_value=0, value=0, step=1)
verbs_edited = st.sidebar.number_input("Verbs Improved", min_value=0, value=0, step=1)
adjectives = st.sidebar.number_input("Adjectives Used", min_value=0, value=0, step=1)
adverbs = st.sidebar.number_input("Adverbs Used", min_value=0, value=0, step=1)
pronouns = st.sidebar.number_input("Pronouns Used", min_value=0, value=0, step=1)
prepositions = st.sidebar.number_input("Prepositions Used", min_value=0, value=0, step=1)
conjunctions = st.sidebar.number_input("Conjunctions Used", min_value=0, value=0, step=1)
interjections = st.sidebar.number_input("Interjections Used", min_value=0, value=0, step=1)
sight = st.sidebar.number_input("Sight Descriptions", min_value=0, value=0, step=1)
smell = st.sidebar.number_input("Smell Descriptions", min_value=0, value=0, step=1)
taste = st.sidebar.number_input("Taste Descriptions", min_value=0, value=0, step=1)
hearing = st.sidebar.number_input("Hearing Descriptions", min_value=0, value=0, step=1)
touch = st.sidebar.number_input("Touch Descriptions", min_value=0, value=0, step=1)

# Writing Calendar
st.sidebar.header("Writing Calendar")
calendar_event = st.sidebar.text_input("Add Writing Event")
calendar_date = st.sidebar.date_input("Select Event Date")
if st.sidebar.button("Add Event"):
    st.session_state.calendar_events.append({"Event": calendar_event, "Date": calendar_date})
    st.sidebar.success("Event Added!")
st.write("## Writing Calendar")
calendar_df = pd.DataFrame(st.session_state.calendar_events)
if not calendar_df.empty:
    st.dataframe(calendar_df)
else:
    st.write("No events added yet.")

# Writing Alarms
st.sidebar.header("Set Writing Alarm")
alarm_time = st.sidebar.time_input("Select Time")
if st.sidebar.button("Set Alarm"):
    st.session_state.alarms.append(alarm_time)
    st.sidebar.success("Alarm Set!")

def check_alarms():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now in [t.strftime("%H:%M") for t in st.session_state.alarms]:
            st.warning(f"⏰ Writing Alarm: Time to write!")
        time.sleep(60)

# Run the alarm checker in a separate thread
alarm_thread = threading.Thread(target=check_alarms, daemon=True)
alarm_thread.start()

# Determine writer level based on words written
def determine_level(total_words):
    if total_words < 26000:
        return f"Beginner Level {min(total_words // 1000 + 1, 25)}"
    elif total_words < 51000:
        return f"Intermediate Level {min((total_words - 25000) // 1000 + 26, 50)}"
    elif total_words < 76000:
        return f"Advanced Level {min((total_words - 50000) // 1000 + 51, 75)}"
    else:
        return f"Professional Level {min((total_words - 75000) // 1000 + 76, 100)}"

if st.sidebar.button("Save Entry"):
    entry = {
        "Date": date,
        "Words": words_written,
        "Sentences": sentences_written,
        "Pages": pages_written,
        "Paragraphs": paragraphs_written,
        "Time Spent (Minutes)": time_spent,
        "Nouns": nouns,
        "Nouns Improved": nouns_edited,
        "Verbs": verbs,
        "Verbs Improved": verbs_edited,
        "Adjectives": adjectives,
        "Adverbs": adverbs,
        "Pronouns": pronouns,
        "Prepositions": prepositions,
        "Conjunctions": conjunctions,
        "Interjections": interjections,
        "Sight Descriptions": sight,
        "Smell Descriptions": smell,
        "Taste Descriptions": taste,
        "Hearing Descriptions": hearing,
        "Touch Descriptions": touch,
        "Writing Text": writing_text
    }
    st.session_state.writing_data.append(entry)
    st.sidebar.success("Entry Saved!")

# Convert to DataFrame
if st.session_state.writing_data:
    df = pd.DataFrame(st.session_state.writing_data)
    st.write("## Writing Progress Data")
    st.dataframe(df)
    
    total_words = df["Words"].sum()
    writer_level = determine_level(total_words)
    st.write(f"### Writer Level: {writer_level}")
