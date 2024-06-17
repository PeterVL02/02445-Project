import os
import data_structure as ds
import logging

import openai 
  

openai.api_key = '<API_KEY>'
logging.basicConfig(level=logging.INFO)

_prompt = """
< PROMPT >
"""

MALE_NAMES = [
    'James',
    'Michael',
    'Robert',
    'John',
    'David',
    'William',
    'Richard',
    'Joseph',
    'Thomas',
    'Christopher'
]
FEMALE_NAMES = [
    'Mary',
    'Patricia',
    'Jennifer',
    'Linda',
    'Elizabeth',
    'Barbara',
    'Susan',
    'Jessica',
    'Karen',
    'Sarah'
]

class DataExtractor:
    def __init__(self, name: str, gender: ds.Gender, round_: int = 2):
        self.name = name
        self.response = None
        self.gender = gender
        self.round_ = round_

    def generate_prompt(self) -> str:
        global _prompt
        return _prompt.replace('[NAME]', self.name).replace('[NAME_Lower]', self.name.lower())


    ## TODO: 
    ## Viet får det til at virke
    ## Definér MaxToken, hardcode om nødvendigt
    ## Husk at åbne ny chat hver gang, helst privat
    ## Brug self.generate_prompt() til at generere prompt
    ## Brug self.save_response(response) response er konverteret til string
    def post_prompt(self, MaxToken: int =50) -> str: 
        response = openai.Completion.create( 

            model='gpt-3.5-turbo',  
            prompt=self.generate_prompt(),  
            max_tokens=MaxToken, 

            n=1
        ) 

        self.response = response.choices[0]['text'].strip()
        self.save_response(self.response)
        return self.response
    
    
    
    def extract_values(self) -> dict | None:
        values = self.extract_helper()
        if values is None: 
            logging.critical(f"Failed to extract values for {self.name}")
            self.save_failed_response(self.response)
            return None
        
        if len(values) != 2:
            logging.critical(f"More than 2 values extracted for {self.name}")
            self.save_failed_response(self.response)
            return None
        
        else:
            self.save_success_response(self.response)
            return {'current': min(values),
                    'deserved' : max(values)}
        
    def push_to_db(self):
        values = self.extract_values()
        if values:
            entry = ds.Entry(name=self.name,
                             gender=self.gender,
                                current_salary=values['current'],
                                deserved_salary=values['deserved'],
                                round_=self.round_)
            ds.commit('GPT', entry)

    def fuckit(self):
        self.post_prompt()
        self.push_to_db()

    def extract_helper(self) -> list[int] | None:
        resp_list = self.response.split()
        values = []
        for word in resp_list:
            if '$' in word:
                if '-' in word:
                    return None
                dig_str = ''
                for char in word:
                    if char.isdigit():
                        dig_str += char
                values.append(int(dig_str) / 1000)
        return values

    def save_response(self,response: str):
        """
        Save the response
        """
        n = len(os.listdir('responses/all_resp')) + 1
        with open(f'responses/all_resp/resp{n}.txt', 'w') as f:
            f.write(response)

    def save_failed_response(self,response: str):
        """
        Save the failed response
        """
        n = len(os.listdir('responses/failed_resp')) + 1
        with open(f'responses/failed_resp/failed_resp{n}.txt', 'w') as f:
            f.write(response)

    def save_success_response(self,response: str):
        """
        Save the success response
        """
        n = len(os.listdir('responses/success_resp')) + 1
        with open(f'responses/success_resp/success_resp{n}.txt', 'w') as f:
            f.write(response)



if __name__ == '__main__':
    extractor = DataExtractor(name = "James",
                              gender = ds.Gender.Male,
                                round_ = 2)
    extractor.fuckit()