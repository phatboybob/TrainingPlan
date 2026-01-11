'''
Mt. Baker Workout App Created for tracking workouts and completion status
with comments.

Notes on updating credentials:
I got the information on how to deploy this with gcp here:
https://docs.streamlit.io/develop/tutorials/databases/private-gsheet

And to update the URL to include any new url redirects I got the info here:
https://console.cloud.google.com/apis/credentials?project=flashcards-475119

Created by Lori Jackson January 2026
'''
from datetime import datetime

import streamlit as st

from utils import (get_calendar_dataframe,
                   login_screen,
                   get_workout,
                   get_comment,
                   get_completion_status,
                   update_header,
                   set_completion_status_emoji,
                   write_df_to_google_drive,
                   )

YES = ":white_check_mark:"
NO = ":x:"
KIND_OF = ":woman_shrugging:"

# Assure the user is logged in and authorized
if not st.user.is_logged_in:
    login_screen()
elif st.user.email not in st.secrets["authorized_users"]:
    st.header(f"Access Denied {st.user.name}")
    st.subheader(f"{st.user.email} does not have permission to view this app.")
else:
    st.header(f"Welcome, {st.user.name}!")
    st.session_state.current_user = st.user.given_name

    # Standard streamlit page configuration
    st.set_page_config(page_title='Mt. Baker Training Plan 2026',
                       layout='wide',
                      )

    # Get the dataframe for the trainingplan only
    if 'calendar_df' not in st.session_state:
        st.session_state.calendar_df = get_calendar_dataframe()

    # Set the current user (based on login information)
    if 'current_user' not in st.session_state:
        st.session_state.current_user = st.user.given_name

    if 'df_written_to_gsheets_text' not in st.session_state:
        st.session_state.df_written_to_gsheets_text = 'Click Submit to write you workout completion status to google sheets'

    # create tabs for the workout and displaying the entire schedule as a dataframe/table
    current_workout_tab, entire_schedule_tab = st.tabs(['Workout', 'Entire Schedule'])

    # Current workout tab: displays the workout for selected date
    # Lets user set if they completed it or not.
    with current_workout_tab:

        # display_date: whatever date is selected
        if 'display_date' not in st.session_state:
            st.session_state.display_date = datetime.now()

        # Version of the date that isn't ugly.
        display_pretty = st.session_state.display_date.strftime('%A, %B %d, %Y')

        if 'display_date_text' not in st.session_state:
            st.session_state.display_date_text = display_pretty

        # version of the data the matches the dataframe date (also the index)
        display_logical = st.session_state.display_date.strftime("%-m/%-d/%Y")

        workout = get_workout(display_logical)

        if 'workout_md' not in st.session_state:
            st.session_state.workout_md = workout

        if 'disable_prior_date_button' not in st.session_state:
            st.session_state.disable_prior_date_button = False
        if 'disable_next_date_button' not in st.session_state:
            st.session_state.disable_next_date_button = False

        if 'completion_status_emoji' not in st.session_state:
            completion_status = get_completion_status(display_logical)
            set_completion_status_emoji(completion_status)


         # Date Navigation Buttons and Header
        prior_date_col, display_date_col, next_day_col, today_col = st.columns(4)
        with prior_date_col:
            st.button('See Prior Day\'s Workout',
                      on_click=update_header, args=(1, 'prior'),
                      disabled=st.session_state.disable_prior_date_button)
        with display_date_col:
            st.header(f"{st.session_state.completion_status_emoji} **Workout for {st.session_state.display_date_text}**")
        with next_day_col:
            st.button('See Next Day\'s Workout',
                      on_click=update_header, args=(1, 'next'),
                      disabled=st.session_state.disable_next_date_button)
        with today_col:
            st.button('Return to Today', on_click=update_header, args=(0, 'today'))


        completion_status = get_completion_status(display_logical)
        comment = get_comment(display_logical)

        col_1, workout_col, col_3 = st.columns(3)
        with col_1:
            st.write("")
        with workout_col:
            st.markdown(st.session_state.workout_md)
        with col_3:
            st.write("")


        completed = st.radio(
            "Did you complete the workout?",
            [f"Yes {YES}", f"No {NO}", f"Kinda {KIND_OF}"],
        )
        explaination = ""
        if completed == f"Yes {YES}":
            completion_status = "Completed"
        elif completed == f"No {NO}":
            completion_status = "Not Completed"
        else:
            completion_status = "Partially Completed"
            explaination = st.text_area("Please explain what you were able to complete:")
        set_completion_status_emoji(completion_status)
        with st.form("Submit Workout Status"):
            submit_to_spreadsheet = st.form_submit_button("Submit Status")
            if submit_to_spreadsheet:
                st.session_state.calendar_df.loc[display_logical, f'{st.session_state.current_user} Completed'] = completion_status
                st.session_state.calendar_df.loc[display_logical, f'{st.session_state.current_user} Comment'] = explaination
                write_df_to_google_drive(st.session_state.calendar_df, completion_status=completion_status, comment=explaination)
                update_header(date_delta=0)
            st.write(st.session_state.df_written_to_gsheets_text)
    with entire_schedule_tab:
        st.markdown('# Currently Viewing the entire schedule')
        st.table(st.session_state.calendar_df)



if st.user.is_logged_in:
    if st.button("Log out"):
        st.logout()
