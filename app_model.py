from flask import Flask, request
import os
import pickle
from sklearn.model_selection import cross_val_score
import pandas as pd
import sqlite3


os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route("/", methods=['GET'])
def hello():
    return "Bienvenido a mi API del modelo advertising"


# 1. Wndpoint que devuelva la predicción de los nuevos datos enviados mediante argumentos en la llamada
@app.route('/v1/predict', methods=['GET'])
def predict():
    model = pickle.load(open('data/advertising_model','rb'))

    tv = request.args.get('tv', None)
    radio = request.args.get('radio', None)
    newspaper = request.args.get('newspaper', None)

    if tv is None or radio is None or newspaper is None:
        return "Missing args, the input values are needed to predict"
    else:
        prediction = model.predict([[tv,radio,newspaper]])
        return "The prediction of sales investing that amount of money in TV, radio and newspaper is: " + str(round(prediction[0],2)) + 'k €'


# 2. To save new registers in the database
@app.route('/v1/add_register', methods= ['GET'])
def add_registers_db():
    new_entry = request.args.to_dict()
    if new_entry == {}:
        return 'No new data to add'
    else:
        tv = float(new_entry['TV'])
        radio = float(new_entry['radio'])
        newspaper = float(new_entry['newspaper'])
        sales = float(new_entry['sales'])

        connection = sqlite3.connect('data/advertising_model_data.db')
        cur = connection.cursor()
        cur.execute("INSERT INTO advertising (TV, radio, newspaper, sales) VALUES (?, ?, ?, ?)",
                    (tv, radio, newspaper, sales))
        connection.commit()
        connection.close()
    return 'New data added successfully'



# 3. Retrain the model on the new data
@app.route('/v1/retrain', methods=['GET'])
def retrain_model():

    # load in the existing model
    model = pickle.load(open('data/advertising_model','rb'))

    # connect and load in full dataset
    connection = sqlite3.connect('data/advertising_model_data.db')
    fetch_table = '''SELECT * FROM advertising'''
    data = pd.read_sql(fetch_table, connection, index_col = 'index', coerce_float = True)

    # split the X and y
    X = data.drop(columns = ['sales'])
    y = data['sales']
    model.fit(X, y)
    cv_score = cross_val_score(model, X, y)

    # save the new model
    with open('advertising_model_v2', 'wb') as f:
        pickle.dump(model, f)

    return f'Model retrained with the latest data and has a cross_val_score of {cv_score}'



#app.run()