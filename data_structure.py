import os
from dotenv import load_dotenv
from enum import Enum
import pickle
import pandas as pd

load_dotenv()

class Gender(Enum):
    """
    Unfortunately relatively narrow at the moment
    """
    Male = 0
    Female = 1

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
    
def get_entry(df: pd.DataFrame, index: int) -> Entry:
    """
    Get the entry at the given index
    """

    return Entry(df.iloc[index]['name'], df.iloc[index]['gender'], 
                 df.iloc[index]['current_salary'], df.iloc[index]['deserved_salary'], 
                 df.iloc[index]['round_'])


def get_id(name: str) -> int:
    """
    Get the id of the given name from the .env file
    """
    name = name.upper()
    identifyer = int(os.getenv(name))
    return identifyer

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

def commit(user: str, entry: Entry) -> None:
    """
    Commit an entry to the appropriate database
    """
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


    

if __name__ == '__main__':
    entry1 = Entry(name='Maria',
                   gender=Gender.Female,
                   current_salary=1000,
                     deserved_salary=2000,
                        round_=1)
    
    commit('Peter', entry1)