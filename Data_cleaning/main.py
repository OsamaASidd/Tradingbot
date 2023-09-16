import pandas as pd

from lxml import html
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import re
import json
import spacy

nlp = spacy.load("en_core_web_sm")


def extract_laws_from_text(text):
    
    doc = nlp(text)
    laws = []

    for ent in doc.ents:
        if ent.label_ == "LAW":
            laws.append(ent.text)
    
    laws = list(set(laws))
    return laws


def extract_text_from_html(html_content):
    
    parsed_html = html.fromstring(html_content)
    
   
    div_texts = parsed_html.xpath('//div//text()')
    
    text_content = " ".join(div_texts)
    cleaned_text = text_content.replace('\r\n', ' ')
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = cleaned_text.rstrip()    
    return cleaned_text


def load_data_from_database(table_name):
    try:
        
        engine = create_engine("mysql+pymysql://root:@localhost/taxin_revivedtaxindia_new1",pool_size=10, max_overflow=20)

        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, engine)

        return df

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def dataframe_to_mysql(dataframe):
    try:
        
        engine = create_engine("mysql+pymysql://root:@localhost/taxin_revivedtaxindia_new1", pool_size=10, max_overflow=20)
        table_name = 'tbl_search_content_cleaned'

        
        Session = sessionmaker(bind=engine)
        session = Session()

        create_table_sql = text(f"CREATE TABLE IF NOT EXISTS `{table_name}` (" \
            "`Id` INT(15) NOT NULL, " \
            "`Clean_text` TEXT NULL DEFAULT NULL, " \
            "`laws` TEXT NULL DEFAULT NULL, " \
            "PRIMARY KEY (`Id`)" \
            ") ENGINE = InnoDB;")

        session.execute(create_table_sql)
        session.commit()
        print(f"Table '{table_name}' has been successfully created in the taxin_revivedtaxindia_new1.")

        for index, row in dataframe.iterrows():
            id = row['Id']
            Clean_text = row['Clean_text']
            laws = ', '.join(row['laws'])

            
            

            insert_data_sql = text(f"INSERT INTO `{table_name}` (`Id`, `Clean_text`, `laws`) " \
                "VALUES (:Id, :Clean_text, :laws)")
            session.execute(insert_data_sql, params={'Id': id, 'Clean_text': Clean_text, 'laws': laws})
            
        session.commit()
        print(f"DataFrame has been successfully converted to the '{table_name}' table in the database.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        if session:
            session.close()


if __name__ == "__main__":
    original_table_name = 'tbl_search_content'  
    df = load_data_from_database(original_table_name)
    new_df = df[['Id', 'Content']]
    new_df = new_df.rename(columns={'Content': 'Judgement'})
    new_df['Clean_text'] = new_df['Judgement'].apply(lambda x: extract_text_from_html(x.decode('utf-8')))
    new_df['laws'] = new_df['Clean_text'].apply(extract_laws_from_text)
    fin_df= new_df[['Id', 'Clean_text', 'laws']]
    fin_df = fin_df.sort_values(by='Id')
    dataframe_to_mysql(fin_df)

    
    
    

    
    

