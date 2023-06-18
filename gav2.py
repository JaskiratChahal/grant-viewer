"""
# Grant App Viewer 2
# Starting from an already downloaded .zip which is unzipped to .xml
# Source code from foa-finder: https://github.com/ericmuckley/foa-finder/
"""

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import streamlit as st
import xml.etree.ElementTree as ET

pd.options.mode.chained_assignment = None

st.title("Grant Application Viewer Demo")
st.markdown("This is a demo of the `foa-finder` application. (Data courtesy of [grants.gov](https://www.grants.gov/).)")
st.header("Data:")

filename = 'GrantsDBExtract{}v2.xml'.format(datetime.today().strftime('%Y%m%d'))
tree = ET.parse("unzipped/{}".format(filename))
doc = str(ET.tostring(tree.getroot(), encoding='unicode', method='xml'))
soup = BeautifulSoup(doc, 'lxml')
print('Database unzipped')

def soup_to_df(soup):
    """Convert beautifulsoup object from grants.gov XML into dataframe"""
    # list of bs4 FOA objects
    s = 'opportunitysynopsisdetail'
    foa_objs = [tag for tag in soup.find_all() if s in tag.name.lower()]

    # loop over each FOA in the database and save its details as a dictionary
    dic = {}
    for i, foa in enumerate(foa_objs):
        ch = foa.findChildren()
        dic[i] = {fd.name.split('ns0:')[1]: fd.text for fd in ch}

    # create dataframe from dictionary
    df = pd.DataFrame.from_dict(dic, orient='index')
    return df


# get full dataframe of all FOAs
df = soup_to_df(soup)


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

# include only FOAs which are not closed
df = df[[is_open(i) for i in df['closedate']]]

# sort by newest FOAs at the top
df = sort_by_recent_updates(df)

st.write(df)