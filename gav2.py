"""
# Grant App Viewer 2
# Starting from a pickle (.pkl) file
# Source code from foa-finder: https://github.com/ericmuckley/foa-finder/
"""

from datetime import datetime
import pandas as pd
import streamlit as st

def to_date(date_str):
    """Convert date string from database into date object"""
    return datetime.strptime(date_str, '%m%d%Y').date()


def is_recent(date, days=14):
    """Check if date occured within n amount of days from today"""
    return (datetime.today().date() - to_date(date)).days <= days


def is_open(date):
    """Check if FOA is still open (closedate is in the past)"""
    if type(date) == float:
        return True
    elif type(date) == str:
        return (datetime.today().date() - to_date(date)).days <= 0


def reformat_date(s):
    """Reformat the date string with hyphens so its easier to read"""
    s = str(s)
    return s[4:]+'-'+s[:2]+'-'+s[2:4]


def sort_by_recent_updates(df):
    """Sort the dataframe by recently updated dates"""
    new_dates = [reformat_date(i) for i in df['lastupdateddate']]
    df.insert(1, 'updatedate', new_dates)
    df = df.sort_values(by=['updatedate'], ascending=False)
    print('Database sorted and filtered by date')
    return df

pd.options.mode.chained_assignment = None

st.title("Grant Application Viewer Demo")
st.markdown("This is a demo of the `foa-finder` application. (Data courtesy of [grants.gov](https://www.grants.gov/).)")
st.header("Data:")

# get full dataframe of all FOAs
df = pd.read_pickle('data-2023-06-18.pkl')

# include only FOAs which are not closed
df = df[[is_open(i) for i in df['closedate']]]

# sort by newest FOAs at the top
df = sort_by_recent_updates(df)

st.write(df)