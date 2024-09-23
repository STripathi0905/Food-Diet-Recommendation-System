from flask import Flask, render_template, request
import pickle
import pandas as pd
import csv
import random

app = Flask(__name__)

# Load the model and food data
with open('food_model.pickle', 'rb') as file:
    model = pickle.load(file)

food_data = pd.read_csv('done_food_data.csv')

def read_csv(file_path, sort_by='Descrip'):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        sorted_rows = sorted(rows, key=lambda x: x[sort_by])
    return sorted_rows

@app.route("/")
def index():
    return render_template("frontpage.html")

@app.route("/predict", methods=['POST'])
def predict():
    try:
        inputs = [
            float(request.form['input_1']),
            float(request.form['input_2']),
            float(request.form['input_3'])
        ]
        prediction = model.predict([inputs])[0]

        result_map = {
            'Muscle_Gain': 'Muscle Gain',
            'Weight_Gain': 'Weight Gain',
            'Weight_Loss': 'Weight Loss'
        }
        result = result_map.get(prediction, 'General food')

        return render_template("frontpage.html", result=result)
    except Exception as e:
        return str(e)

def filter_food_data(category, preferences):
    filtered_data = food_data[food_data['category'] == category]

    if 'iron' in preferences:
        filtered_data = filtered_data[filtered_data['Iron_mg'] > 6]
    if 'calcium' in preferences:
        filtered_data = filtered_data[filtered_data['Calcium_mg'] > 150]

    exclude_keywords = [
        'Egg', 'Fish', 'meat', 'beef', 'Chicken', 'Beef', 'Deer', 'lamb', 'crab', 'pork', 
        'Turkey', 'flesh', 'Ostrich', 'Emu', 'cuttlefish', 'Seaweed', 'crayfish', 'shrimp', 'Octopus'
    ]

    if 'vegetarian' in preferences:
        filtered_data = filtered_data[~filtered_data['Descrip'].str.contains('|'.join(exclude_keywords), case=False)]

    if 'non_vegetarian' in preferences:
        filtered_data = filtered_data[filtered_data['Descrip'].str.contains('|'.join(exclude_keywords), case=False)]

    return filtered_data['Descrip'].sample(n=min(5, len(filtered_data))).to_string(index=False)

@app.route("/musclegain", methods=['POST'])
def musclegain():
    preferences = request.form.getlist('preferences')
    if 'anyfoods' in preferences:
        musclegainfoods = food_data[food_data['category'] == 'Muscle_Gain']['Descrip'].sample(n=5).to_string(index=False)
    else:
        musclegainfoods = filter_food_data('Muscle_Gain', preferences)

    return render_template("frontpage.html", musclegainfoods=musclegainfoods)

@app.route("/weightgain", methods=['POST'])
def weightgain():
    preferences = request.form.getlist('preferences')
    if 'anyfoods' in preferences:
        weightgainfoods = food_data[food_data['category'] == 'Weight_Gain']['Descrip'].sample(n=5).to_string(index=False)
    else:
        weightgainfoods = filter_food_data('Weight_Gain', preferences)

    return render_template("frontpage.html", weightgainfoods=weightgainfoods)

@app.route("/weightloss", methods=['POST'])
def weightloss():
    preferences = request.form.getlist('preferences')
    if 'anyfoods' in preferences:
        weightlossfoods = food_data[food_data['category'] == 'Weight_Loss']['Descrip'].sample(n=5).to_string(index=False)
    else:
        weightlossfoods = filter_food_data('Weight_Loss', preferences)

    return render_template("frontpage.html", weightlossfoods=weightlossfoods)

@app.route("/search", methods=['POST'])
def search():
    sort_by = request.form.get('sort_by', 'Descrip')
    rows = read_csv('done_food_data.csv', sort_by)
    return render_template('search.html', rows=rows)

if __name__ == "__main__":
    app.run()
