"""
Utilities for the Streamlit Mt. Baker Workout Plan App
Created by Lori Jackson January 2026
"""

from datetime import datetime, timedelta

import streamlit as st
from streamlit_gsheets import GSheetsConnection
from time import strftime

YES = ":white_check_mark:"
NO = ":x:"
KIND_OF = ":woman_shrugging:"

CALENDAR_WORKSHEET = 'Schedule_streamlit'
WORKOUTS_WORKSHEET = 'Workouts'
COLUMNS_AND_TYPES = {'Date': datetime,
                     'Day of the Week': str,
                     'Workout': str,
                     'Lori Completed': str,
                     'Lori Comment': str,
                     'Jonathan Completed': str,
                     'Jonathan Comment': str,
                     'Miriam Completed': str,
                     'Miriam Comment': str,
                     }

COLUMN_DTYPES = {
                 'Day of the Week': 'string',
                 'Workout': 'string',
                 'Lori Completed': 'string',
                 'Lori Comment': 'string',
                 'Jonathan Completed': 'string',
                 'Jonathan Comment': 'string',
                 'Miriam Completed': 'string',
                 'Miriam Comment': 'string',
                }

NA_VALUES = ["No Value"]

COLUMN_CONFIG = {
                'Date': st.column_config.DateColumn(
                        "Date of Workout",
                        help="Date of the workout",
                        format=strftime("MM/DD/YYYY"),
                ),
                'Day of Week': st.column_config.TextColumn(
                    "Day of the Week",
                    help="Day of the week for the workout",
                ),
                'Workout': st.column_config.TextColumn(
                    "Workout Description",
                    help="Description of the workout",
                ),
                'Lori Completed': st.column_config.TextColumn(
                    "Lori Completed?",
                    help="Did Lori complete the workout?",
                ),
                'Lori Comment': st.column_config.TextColumn(
                    "Lori's Comments",
                    help="Lori's comments on the workout",
                ),
                'Jonathan Completed': st.column_config.TextColumn(
                    "Jonathan Completed?",
                    help="Did Jonathan complete the workout?",
                ),
                'Jonathan Comment': st.column_config.TextColumn(
                    "Jonathan's Comments",
                    help="Jonathan's comments on the workout",
                ),
                'Miriam Completed': st.column_config.TextColumn(
                    "Miriam Completed?",
                    help="Did Miriam complete the workout?",
                ),
                'Miriam Comment': st.column_config.TextColumn(
                    "Miriam's Comments",
                    help="Miriam's comments on the workout",
                ),
        }

def update_header(date_delta=0, direction='None'):
    st.session_state.disable_next_date_button = False
    st.session_state.disable_prior_date_button = False
    if direction == 'prior':
        st.session_state.display_date -= timedelta(days=date_delta)
    elif direction == 'next':
        st.session_state.display_date += timedelta(days=date_delta)
    elif direction == 'today':
        st.session_state.display_date = datetime.today()
    else:
        st.session_state.display_date += timedelta(days=0)
    display_pretty = st.session_state.display_date.strftime('%A, %B %d, %Y')
    display_logical = st.session_state.display_date.strftime("%-m/%-d/%Y")
    st.session_state.workout_md = get_workout(display_logical)
    st.session_state.display_date_text = display_pretty
    set_completion_status_emoji(get_completion_status(display_logical))
    try:
        temp_date = st.session_state.display_date - timedelta(days=1)
        display_logical = temp_date.strftime("%-m/%-d/%Y")
        _ = get_workout(display_logical)
    except KeyError:
        st.session_state.disable_prior_date_button = True
    try:
        temp_date = st.session_state.display_date + timedelta(days=1)
        display_logical = temp_date.strftime("%-m/%-d/%Y")
        _ = get_workout(display_logical)
    except KeyError:
        st.session_state.disable_next_date_button = True


def get_calendar_dataframe():
    """Uploads a csv and returns it as a dataframe

    Args:
        flashcard_path (path, optional): path to a csv. Defaults to LORIS_FLASHCARDS_CSV.

    Returns:
        dataframe: dataframe conversion of the csv
    """

    # Create a connection object.
    gcp_connection = st.connection("gsheets",
                                   type=GSheetsConnection)

    na_fill_subeset = {'Workout': 'Lori hasn\'t Figured it out yet. Damn.',
                       'Lori Completed': 'Not Completed',
                       'Lori Comment': '',
                       'Jonathan Completed': 'Not Completed',
                       'Jonathan Comment': '',
                       'Miriam Completed': 'Not Completed',
                       'Miriam Comment': '',
                       }
    calendar_df = gcp_connection.read(worksheet=CALENDAR_WORKSHEET, index_col='Date', parse_dates=['Date'], dtype=COLUMN_DTYPES).fillna(na_fill_subeset)

    return calendar_df


def get_workout_descriptions_dataframe():
    """Gets the workouts dataframe from Google Sheets

    Returns:
        dataframe: dataframe conversion of the csv of workouts
    """

    # Create a connection object.
    gcp_connection = st.connection("gsheets",
                                   type=GSheetsConnection)

    na_fill_subeset = {'URL': '',
                       }
    workouts_df = gcp_connection.read(worksheet=WORKOUTS_WORKSHEET, index_col='Workout Name').fillna(na_fill_subeset).dropna(how='all')

    return workouts_df

def get_workout(date):
    """Gets today's workout from the calendar dataframe

    Args:
        today (string): today's date in '???' format

    Returns:
        string: today's workout
    """
    todays_workout = st.session_state.calendar_df.loc[date, 'Workout']
    return todays_workout

def get_completion_status(date, user='Lori'):
    """Gets today's workout completion status from the calendar dataframe

    Args:
        today (string): today's date in '???' format
    """
    completion_status = st.session_state.calendar_df.loc[date, f'{user} Completed']
    return completion_status

def set_completion_status_emoji(completion_status):
    if completion_status == "Completed":
        st.session_state.completion_status_emoji = YES
    elif completion_status == "Not Completed":
        st.session_state.completion_status_emoji = NO
    else:
        st.session_state.completion_status_emoji = KIND_OF

def get_comment(date, user='Lori'):
    """Gets today's workout comment from the calendar dataframe

    Args:
        today (string): today's date in '???' format
    """
    comment = st.session_state.calendar_df.loc[date, f'{user} Comment']
    return comment



def update_correct_word(direction, from_word, df):
    """updates when a word is correct
    Args:
        direction (string): Same as all the others of this
        from_word (string): word that user tried to translate
        df (Datframe): Dataframe containing the sample flashcard data.
            ie, what needs to be updated.
    """

    # get the current number of times user has answered correctly
    correct_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Correct Count']

    # get the current number of times the user has been asked this word
    call_count = df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count']

    correct_count += 1
    call_count += 1
    correct_percent = correct_count/call_count * 100

    # update sample dataframe with new counts and percent correct
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Call Count'] = call_count
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Correct Count'] = correct_count
    df.loc[df[f'{direction} Word'] == from_word, f'{direction} Percent Correct'] = correct_percent


def write_df_to_google_drive(dataframe, completion_status='Nothing', comment ='Nothing'):
    """writes a dataframe to Google Drive
    """
    # sheet_name = get_flashcard_worksheet_by_user(user)
    conn = st.connection("gsheets", type=GSheetsConnection)
    display_pretty = st.session_state.display_date.strftime('%A, %B %d, %Y')
    st.session_state.df_written_to_gsheets_text = f"Status of '{completion_status}' with comment '{comment}' for {display_pretty} has been written to Google Sheets."
    conn.update(
        worksheet=CALENDAR_WORKSHEET,
        data=dataframe.reset_index(),
    )

def disable_yes_no():
    """disable any buttons with the session state of 'disabled' (yes and no)
    """
    if 'disabled' in st.session_state and st.session_state.disabled is True:
        st.session_state.disabled = False


def enable_buttons():
    """Enable any buttons with the session state of 'disabled' (yes and no)
    """
    st.session_state.yes_no_disabled = False

def disable_buttons():
    """Disable any buttons with the session state of 'disabled' (yes and no)
    enables submit button. I don't like this but it works and buttons are HARD
    """
    st.session_state.yes_no_disabled = True
    st.session_state.submit_button_disabled = False


def switch_buttons():
    """switches the yes/no and the submit buttons state from
    enabled (clickable) to disablee (not clickable.)
    """
    st.session_state.yes_no_disabled = not st.session_state.yes_no_disabled
    st.session_state.submit_button_disabled = not st.session_state.yes_no_disabled

def login_screen():
    """Displays the login screen
    """
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)