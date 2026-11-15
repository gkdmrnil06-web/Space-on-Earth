"""Local Space on Earth authentication prototype (not production authentication).

Only use for localhost demos with test accounts. Password hashes are stored with
Argon2id; identity/email ownership is not verified. Do not use real passwords.
"""
from i18n import t
from pathlib import Path
import re
import sqlite3
import time
import streamlit as st
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
try:
    from argon2.exceptions import InvalidHashError
except ImportError:
    from argon2.exceptions import InvalidHash as InvalidHashError
DB_FILE = Path(__file__).resolve().parent / 'space_on_earth_users.db'
HASHER = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
MAX_ATTEMPTS = 5
LOCK_SECONDS = 300

def connect_db():
    connection = sqlite3.connect(DB_FILE, timeout=10)
    connection.execute('PRAGMA busy_timeout = 10000')
    connection.execute('CREATE TABLE IF NOT EXISTS users (\n        email TEXT PRIMARY KEY,\n        password_hash TEXT NOT NULL,\n        failed_attempts INTEGER NOT NULL DEFAULT 0,\n        locked_until INTEGER NOT NULL DEFAULT 0\n    )')
    connection.commit()
    return connection

def normalize_email(email):
    return email.strip().lower()

def valid_email(email):
    return len(email) <= 254 and re.fullmatch('[^@\\s]+@[^@\\s]+\\.[^@\\s]+', email) is not None

def create_account(email, password):
    if not valid_email(email) or not 12 <= len(password) <= 128:
        return False
    password_hash = HASHER.hash(password)
    with connect_db() as connection:
        try:
            connection.execute('INSERT INTO users(email, password_hash) VALUES (?, ?)', (email, password_hash))
        except sqlite3.IntegrityError:
            return False
    return True

def authenticate(email, password):
    now = int(time.time())
    with connect_db() as connection:
        record = connection.execute('SELECT password_hash, failed_attempts, locked_until FROM users WHERE email=?', (email,)).fetchone()
        if record is None:
            return False
        stored_hash, failures, locked_until = record
        if locked_until > now:
            return False
        try:
            HASHER.verify(stored_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            failures += 1
            until = now + LOCK_SECONDS if failures >= MAX_ATTEMPTS else 0
            connection.execute('UPDATE users SET failed_attempts=?, locked_until=? WHERE email=?', (failures, until, email))
            return False
        connection.execute('UPDATE users SET failed_attempts=0, locked_until=0 WHERE email=?', (email,))
        return True

def require_access():
    """Called by app.py; stops rendering until the user chooses an access mode."""
    if 'access_mode' not in st.session_state:
        st.session_state.access_mode = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if st.session_state.access_mode is None:
        st.title(t('🌍 Welcome to Space on Earth'))
        st.caption(t('Local research prototype — do not use an existing personal password.'))
        signin, signup = st.tabs([t('Log In'), t('Sign Up')])
        with signin:
            with st.form('login_form'):
                email = st.text_input(t('Email address'), key='login_email')
                password = st.text_input(t('Password'), type='password', key='login_password')
                submitted = st.form_submit_button(t('Log In'), use_container_width=True)
            if submitted:
                if authenticate(normalize_email(email), password):
                    st.session_state.access_mode = 'account'
                    st.session_state.user_email = normalize_email(email)
                    st.rerun()
                else:
                    st.error(t('Invalid credentials or temporarily locked account.'))
        with signup:
            with st.form('signup_form'):
                email = st.text_input(t('Email address'), key='signup_email')
                password = st.text_input(t('Create password (12+ characters)'), type='password', key='signup_password')
                confirm = st.text_input(t('Confirm password'), type='password', key='signup_confirm')
                submitted = st.form_submit_button(t('Create Account'), use_container_width=True)
            if submitted:
                normalized = normalize_email(email)
                if password != confirm:
                    st.error(t('Passwords do not match.'))
                elif not valid_email(normalized):
                    st.error(t('Enter a valid email address format.'))
                elif not 12 <= len(password) <= 128:
                    st.error(t('Use a password between 12 and 128 characters.'))
                elif create_account(normalized, password):
                    st.success(t('Local account created. Open Log In to sign in.'))
                else:
                    st.error(t('Unable to create account. Try a different email.'))
        st.divider()
        if st.button(t('Continue as Guest'), use_container_width=True):
            st.session_state.access_mode = 'guest'
            st.session_state.user_email = None
            st.rerun()
        st.info(t('Demo only: emails are not verified. Accounts are stored only on this computer. Not suitable for public deployment.'))
        st.stop()
    with st.sidebar:
        if st.session_state.access_mode == 'account':
            st.write(t('Signed in:'), st.session_state.user_email)
        else:
            st.write(t('Guest mode'))
        if st.button(t('Log Out')):
            st.session_state.access_mode = None
            st.session_state.user_email = None
            st.rerun()
