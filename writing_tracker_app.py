import streamlit as st
import pandas as pd
import datetime
import time
import threading
import os

# Ensure necessary dependencies are installed
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk import pos_tag
    nltk.download('averaged_perceptron_tagger')
except ModuleNotFoundError:
    os.system("pip install nltk")
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk import pos_tag
    nltk.download('averaged_perceptron_tagger')

# Initialize session state
if 'writing_data' not in st.session_state:
    st.session_state.writing_data = []
if 'alarms' not in st.session_state:
    st.session_state.alarms = []
if 'calendar_events' not in st.session_state:
    st.session_state.calendar_events = []
if 'writing_text' not in st.session_state:
    st.session_state.writing_text = ""
if 'tracking_stats' not in st.session_state:
    st.session_state.tracking_stats = {
        'total_verbs': 0, 'current_verbs': 0, 'verbs_changed': 0,
        'total_nouns': 0, 'current_nouns': 0, 'nouns_changed': 0,
        'total_adjectives': 0, 'current_adjectives': 0, 'adjectives_changed': 0,
        'total_adverbs': 0, 'current_adverbs': 0, 'adverbs_changed': 0
    }
if 'time_stats' not in st.session_state:
    st.session_state.time_stats = {
        'total_hours': 0,
        'daily_hours': {},
        'total_sessions': 0,
        'daily_sessions': {}
    }

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

# Function to update part-of-speech statistics
def update_pos_statistics(new_text, old_text):
    new_tokens = word_tokenize(new_text)
    old_tokens = word_tokenize(old_text)

    new_pos = pos_tag(new_tokens)
    old_pos = pos_tag(old_tokens)

    pos_categories = {
        'VB': 'verbs', 'NN': 'nouns', 'JJ': 'adjectives', 'RB': 'adverbs'
    }

    # Count POS changes
    for new_word, new_tag in new_pos:
        if any(new_tag.startswith(key) for key in pos_categories):
            category = pos_categories[new_tag[:2]]
            st.session_state.tracking_stats[f'total_{category}'] += 1
            st.session_state.tracking_stats[f'current_{category}'] += 1

    for old_word, old_tag in old_pos:
        if any(old_tag.startswith(key) for key in pos_categories):
            category = pos_categories[old_tag[:2]]
            st.session_state.tracking_stats[f'current_{category}'] -= 1

    # Detect changes (e.g., stronger word replacement)
    for new, old in zip(new_pos, old_pos):
        if new[0] != old[0] and new[1].startswith(old[1][:2]):
            category = pos_categories[old[1][:2]]
            st.session_state.tracking_stats[f'{category}_changed'] += 1

# Update statistics when the text changes
if writing_text != st.session_state.writing_text:
    update_pos_statistics(writing_text, st.session_state.writing_text)
    st.session_state.writing_text = writing_text

# Calculate writing statistics
words_written = len(writing_text.split())
sentences_written = writing_text.count('.') + writing_text.count('!') + writing_text.count('?')
pages_written = words_written / 250  # Assuming 250 words per page
paragraphs_written = writing_text.count('\n')
time_spent = st.sidebar.number_input("Time Spent Writing (Minutes)", min_value=0, value=0, step=5)

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

if st.sidebar.button("Save Entry"):
    entry = {
        "Date": date,
        "Words": words_written,
        "Sentences": sentences_written,
        "Pages": pages_written,
        "Paragraphs": paragraphs_written,
        "Tracking Stats": st.session_state.tracking_stats.copy(),
        "Writing Text": writing_text
    }
    st.session_state.writing_data.append(entry)
    st.sidebar.success("Entry Saved!")

# Convert to DataFrame
if st.session_state.writing_data:
    df = pd.DataFrame(st.session_state.writing_data)
    st.write("## Writing Progress Data")
    st.dataframe(df)

# Display current POS tracking stats
st.write("### Part-of-Speech Tracking Statistics")
st.json(st.session_state.tracking_stats)
