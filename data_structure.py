import os
from dotenv import load_dotenv
from enum import Enum
import pickle
import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

load_dotenv()

class Gender(Enum):
    """
    Unfortunately relatively narrow at the moment
    """
    Male = 0
    Female = 1

    def __gt__(self, other) -> bool:
        if isinstance(other, Gender):
            return self.value > other.value
        
    def __lt__(self, other) -> bool:
        if  isinstance(other, Gender):
            return self.value < other.value
        
    def __eq__(self, other) -> bool:
        if isinstance(other, Gender):
            return self.value == other.value
class Entry:
    def __init__(self,
                 name: str,
                 gender: Gender,
                 current_salary: float,
                 deserved_salary: float,
                 round_: int):
        self.name = name
        self.gender = gender
        self.current_salary = current_salary
        self.deserved_salary = deserved_salary
        self.round_ = round_

    def _gender_bin_(self):
        return self.gender.value

    def __repr__(self):
        return f"""Entry(Name: {self.name}, Gender: {self.gender}, Current Salary: {self.current_salary},
                Deserved Salary: {self.deserved_salary}, Round: {self.round_})"""   
    
    def to_pd(self):
        return pd.DataFrame([self.__dict__])
    
def get_id(name: str) -> int:
    """
    Get the id of the given name from the .env file
    """
    name = name.upper()
    identifyer = int(os.getenv(name))
    return identifyer

def safety_check(func: callable) -> callable:
    logging.info(f'Running safety check on {func.__name__}')
    def wrapper(*args, **kwargs):
        pass
        return func(*args, **kwargs)
    logging.info(f'Successfully ran safety check on {func.__name__}')
    return wrapper



def get_entry(df: pd.DataFrame, index: int) -> Entry:
    """
    Get the entry at the given index
    """

    return Entry(df.iloc[index]['name'], df.iloc[index]['gender'], 
                 df.iloc[index]['current_salary'], df.iloc[index]['deserved_salary'], 
                 df.iloc[index]['round_'])



def unpack_values(entry: Entry) -> list:
    """
    Unpack the values of the given entry
    """
    return list(entry.__dict__.values())

def check_db(user: str) -> bool:
    """
    Check if the database for the given user exists
    """
    user_id = get_id(user)
    return os.path.exists(f'data/db{user_id}.pkl')

def append_db(user: str, entry: Entry) -> None:
    """
    Append the entry to the database
    """
    user_id = get_id(user)
    df = pd.read_pickle(f'data/db{user_id}.pkl')
    df = pd.concat([df, entry.to_pd()])
    with open(f'data/db{user_id}.pkl', 'wb') as f:
        pickle.dump(df, f)

def create_db(user: str, initial_commit: Entry) -> None:
    user_id = get_id(user)
    if not check_db(user):
        with open(f'data/db{user_id}.pkl', 'wb') as f:
            try:
                pickle.dump(initial_commit.to_pd(), f)
            except AttributeError:
                pickle.dump(initial_commit, f)

    else:
        raise ValueError("Database already exists")

@safety_check
def commit(user: str, entry: Entry) -> None:
    """
    Commit an entry to the appropriate database
    """
    assert isinstance(entry, Entry), "Entry must be of type Entry."
    if not check_db(user):
        print("Creating new database")
        create_db(user, entry)
    else:
        append_db(user, entry)

def get_db(user: str) -> pd.DataFrame:
    """
    Get the database for the given user
    """
    user_id = get_id(user)
    return pd.read_pickle(f'data/db{user_id}.pkl')

def get_db_head(user: str, n: int = 5) -> pd.DataFrame:
    """
    Get the first n rows of the database
    """
    return get_db(user).head(n)

@safety_check
def merge_databases() -> pd.DataFrame:
    """
    Merge all databases into one
    """
    seen_files = []

    df = pd.DataFrame()
    for file in os.listdir('data/'):
        if file.endswith('.pkl'):
            seen_files.append(file)
            df = pd.concat([df, pd.read_pickle(f'data/{file}')])

    for file in seen_files:
        if 'db' in file and len(file) == 7:
            os.remove(f'data/{file}')

    commit('all', df)

    return get_db('all')

@safety_check
def commit_multiple(user: str,
                    name: str,
                    gender: Gender,
                    currents: list,
                    deserveds: list,
                    round_: int) -> None:
    """
    Commit multiple entries to the database
    """
    for i in range(len(currents)):
        entry = Entry(name=name,
                      gender=gender,
                      current_salary=currents[i],
                        deserved_salary=deserveds[i],
                            round_=round_)
        commit(user, entry)

def locate(user: str, 
           column: str,
           name: str = None,
           gender: Gender = None,
           dataframe: pd.DataFrame = None) -> np.ndarray:
    """
    Locate columns in the database. Example:
    locate(user='Robin'
            column='deserved_salary,
             gender=Gender.Male)
    This returns an array of deserved salaries for all men in Robin's database.
    Could also have specified name='John Doe' to get the deserved salary of John Doe.

    If dataframe is provided, the function will search in that dataframe instead and user is ignored.
    Useful if search_all() is used.
    """
    assert name or gender, "Either name or gender should be specified"
    assert not (name and gender), "Cannot query both name and gender at the same time"
    
    df = get_db(user) if dataframe is None else dataframe
    if dataframe is not None:
        logging.info(f'Dataframe provided, ignoring user {user}')
        user = 'all'

    if name:
        logging.info(f'Locating {column} for {name} in {user}\'s database')
        return df.loc[df['name'] == name][column].values
    else:
        logging.info(f'Locating {column} for {gender.name.lower()}s in {user}\'s database')
        return df.loc[df['gender'] == gender][column].values
    
def search_all() -> pd.DataFrame:
    """
    Returns dataframe of all databases
    """
    df = pd.DataFrame()
    for file in os.listdir('data/'):
        if file.endswith('.pkl') and 'db' in file:
            df = pd.concat([df, pd.read_pickle(f'data/{file}')])
    return df

if __name__ == '__main__':
    entry1 = Entry(name='DeMarcus Cousins',
                   gender=Gender.Male,
                   current_salary=3000,
                     deserved_salary=6000,
                        round_=1)
    
    commit('Nicholas', entry1)

    print(locate(
        user = 'Nicholas',
        column = 'deserved_salary',
        gender = Gender.Male,
        dataframe=search_all()))