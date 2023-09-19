import os
import re
import pandas as pd
from lxml import html
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import spacy
from flask import Flask, jsonify, request, g

app = Flask(__name__)
app.secret_key = "!secret_key"

nlp = spacy.load("en_core_web_sm")

# Database connection engine
engine = create_engine("mysql+pymysql://root:@localhost/taxin_revivedtaxindia_new1", pool_size=10, max_overflow=20)

Session = sessionmaker(bind=engine)

# Create a global database session
@app.before_request
def before_request():
    g.session = Session()

@app.teardown_appcontext
def teardown_appcontext(error=None):
    # Automatically commit and close the session when the app context is torn down
    if hasattr(g, 'session'):
        g.session.commit()
        g.session.close()

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
        query = f"SELECT 'Id', 'Content' FROM {table_name}"
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def dataframe_to_mysql(dataframe, table_name):
    try:
        create_table_sql = text(f"CREATE TABLE IF NOT EXISTS `{table_name}` (" \
            "`Id` INT(15) NOT NULL, " \
            "`Clean_text` TEXT NULL DEFAULT NULL, " \
            "`laws` TEXT NULL DEFAULT NULL, " \
            "PRIMARY KEY (`Id`)" \
            ") ENGINE = InnoDB;")

        g.session.execute(create_table_sql)
        g.session.commit()
        print(f"Table '{table_name}' has been successfully created in the taxin_revivedtaxindia_new1.")

        for index, row in dataframe.iterrows():
            id = row['Id']
            Clean_text = row['Clean_text']
            laws = ', '.join(row['laws'])

            insert_data_sql = text(f"INSERT INTO `{table_name}` (`Id`, `Clean_text`, `laws`) " \
                "VALUES (:Id, :Clean_text, :laws)")
            g.session.execute(insert_data_sql, params={'Id': id, 'Clean_text': Clean_text, 'laws': laws})

        g.session.commit()
        print(f"DataFrame has been successfully converted to the '{table_name}' table in the database.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

@app.route("/<int:CaseId>/text", methods=["GET"])
def get_text(CaseId):
    query = f"SELECT Clean_text FROM tbl_search_content_cleaned WHERE Id = {CaseId}"
    df = pd.read_sql_query(query, engine)

    if df.empty:
        return jsonify({"error": "No data found for the given CaseId"}), 404

    clean_text = df["Clean_text"].iloc[0]

    response_data = {"CaseId": CaseId, "CleanText": clean_text}

    return jsonify(response_data), 200

@app.route("/<int:CaseId>/laws", methods=["GET"])
def get_laws(CaseId):
    query = f"SELECT laws FROM tbl_search_content_cleaned WHERE Id = {CaseId}"
    df = pd.read_sql_query(query, engine)

    if df.empty:
        return jsonify({"error": "No data found for the given CaseId"}), 404

    laws = df["laws"].iloc[0]

    response_data = {"CaseId": CaseId, "Laws": laws}

    return jsonify(response_data), 200

@app.route("/addcase", methods=["POST"])
def add_case():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data provided"}), 400

        CaseId = data["Id"]
        judgement = data["Judgement"]
        Clean_text = extract_text_from_html(judgement)
        laws = extract_laws_from_text(Clean_text)
        insert_data_sql = text(f"INSERT INTO tbl_search_content_cleaned (`Id`, `Clean_text`, `laws`) " \
                "VALUES (:Id, :Clean_text, :laws)")
        g.session.execute(insert_data_sql, params={'Id': CaseId, 'Clean_text': Clean_text, 'laws': ', '.join(laws)})
        return jsonify({"message": "Case added successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    original_table_name = 'tbl_search_content'  
    new_df = load_data_from_database(original_table_name)
    new_df = new_df.rename(columns={'Content': 'Judgement'})
    new_df['Clean_text'] = new_df['Judgement'].apply(lambda x: extract_text_from_html(x.encode('utf-8')))
    new_df['laws'] = new_df['Clean_text'].apply(extract_laws_from_text)
    fin_df = new_df[['Id', 'Clean_text', 'laws']]
    fin_df = fin_df.sort_values(by='Id')
    dataframe_to_mysql(fin_df, 'tbl_search_content_cleaned')
    app.run()
