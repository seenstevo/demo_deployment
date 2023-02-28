import pandas as pd
import sqlite3
import os
from pathlib import Path


os.chdir(os.path.dirname(os.path.abspath(__file__)))

# crate the database
Path('data/advertising_model_data.db').touch()
connection = sqlite3.connect('data/advertising_model_data.db')
c = connection.cursor()
c.execute('''CREATE TABLE advertising
             (row_id integer auto_increment primary key,
              TV float NOT NULL,
              radio float NOT NULL,
              newspaper float NOT NULL,
              sales float NOT NULL)''')
# load the data into a Pandas DataFrame
data = pd.read_csv('data/Advertising.csv', index_col = 0)
# write the data to a sqlite table
data.to_sql('advertising', connection, if_exists = 'append', index = True, index_label = 'row_id')
connection.commit()
connection.close()