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
@app.route('/v2/predict', methods=['GET'])
def predict():
    model = pickle.load(open('data/advertising_model','rb'))

    predict_vals = {k.lower(): float(v) for k, v in request.args.to_dict().items()}

    if len(predict_vals) != 3:
        return f'This model needs 3 fields to make a prediction of sales (TV, radio and newspaper). Please review input and try again'

    else:
        prediction = model.predict([[predict_vals['tv'], predict_vals['radio'], predict_vals['newspaper']]])
        return f'The prediction of sales investing that amount of money in TV, radio and newspaper is: {str(round(prediction[0],2))}k €. {predict_vals}'




# 2. To save new registers in the database
@app.route('/v2/add_register', methods= ['POST'])   # this allows for inserting new data
def add_registers_db():
    new_entry = {k.lower(): v for k, v in request.args.to_dict().items()}
    if len(new_entry) != 4:
        return '4 data fields needed (TV, radio, newspaper, sales). Please check and try again'
    else:
        tv = float(new_entry['tv'])
        radio = float(new_entry['radio'])
        newspaper = float(new_entry['newspaper'])
        sales = float(new_entry['sales'])

        connection = sqlite3.connect('data/advertising_model_data.db')
        cur = connection.cursor()
        cur.execute("INSERT INTO advertising (TV, radio, newspaper, sales) VALUES (?, ?, ?, ?)",
                    (tv, radio, newspaper, sales))
        cur = connection.cursor()
        last_rows = '''SELECT * FROM advertising ORDER BY row_id DESC LIMIT 5;'''
        result = pd.DataFrame(cur.execute(last_rows).fetchall(), columns = ['row_id', 'TV', 'radio', 'newspaper', 'sales']).set_index('row_id')
        result = result.to_html()
        connection.commit()
        connection.close()

    return f'New data added successfully and here are the last 5 rows:\n\n\n{result}'



# 3. Retrain the model on the new data
@app.route('/v2/retrain', methods = ['PUT'])    # this method allows for rewriting
def retrain_model():

    # load in the existing model
    with open('data/advertising_model','rb') as f:
        model = pickle.load(f)

    # connect and load in full dataset
    connection = sqlite3.connect('data/advertising_model_data.db')
    fetch_table = '''SELECT * FROM advertising'''
    data = pd.read_sql(fetch_table, connection, coerce_float = True)

    # split the X and y
    X = data.drop(columns = ['sales', 'row_id']).values
    y = data['sales'].values
    model.fit(X, y)
    cv_score = cross_val_score(model, X, y, cv = 3)

    # save the new model
    with open('data/advertising_model', 'wb') as f:
        pickle.dump(model, f)

    return f'New model saved and retrained with the latest data and has a cross_val_scores (cv=3) of {cv_score}'


#app.run()  # python anywhere needs this to be commented as automatically runs this as app