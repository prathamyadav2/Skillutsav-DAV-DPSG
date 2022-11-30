from flask import Flask, render_template, request, redirect, url_for, jsonify
import httpx
import json
import pandas as pd
import pickle


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-crop-predicter'
app.config['weather-api-key'] = '5aa0a723b7b373b0b9ed298efcad3431'


def is_internet_connection():
    try:
        httpx.get('https://google.com')
        return True
    except httpx.ConnectError:
        return False


def get_weather(city: str):
	resp = httpx.get('http://api.openweathermap.org/data/2.5/weather', params = { 'q': city, 'appid': app.config['weather-api-key'] }).json()
	temp = resp['main']['temp'] - 273.15
	humidity = resp['main']['humidity']

	return { 'temperature': temp, 'humidity': humidity }


@app.route('/', methods = [ 'GET', 'POST' ])
def home():
	if request.method == 'POST':

		if is_internet_connection():

			with open('./static/datasets/rainfall.json', 'r') as rainfall_db:
				rainfall = json.load(rainfall_db)['data'][request.form.get('state-dropdown').strip()]
			weather = get_weather(city = request.form.get('city-dropdown').strip())
			prediction_data = {
				'N': request.form.get('nitrogen-entry'),
				'P': request.form.get('phosphorus-entry'),
				'K': request.form.get('potassium-entry'),
				'temperature': weather['temperature'],
			   	'humidity': weather['humidity'],
				'ph': request.form.get('ph-entry'),
				'rainfall': rainfall
			}
			prediction_data_dataframe = pd.DataFrame( [ prediction_data ] )

			Model = pickle.load(open('./models/Model.pkl', 'rb'))

			prediction = Model.predict(prediction_data_dataframe)[0]

			pdata_text = '|'.join(
				[
					f"N: {round(float(request.form.get('nitrogen-entry')), 2)}",
					f"P: {round(float(request.form.get('phosphorus-entry')), 2)}",
     				f"K: {round(float(request.form.get('potassium-entry')), 2)}",
					f"pH: {round(float(request.form.get('ph-entry')), 2)}",
					f"Rainfall: {round(float(rainfall), 2)}",
					f"Humidity: {round(float(weather['humidity']), 2)}",
					f"Temperature: {round(float(weather['temperature']), 2)}",
					f"{request.form.get('city-dropdown').title().strip()}, {request.form.get('state-dropdown').title().strip()}, India"
				]
			)
   
			df = pd.read_csv("./static/datasets/raw_data.csv")
			
			if rainfall > 175 and rainfall <250:
				rainfall2 = 1
			if rainfall >= 145 and rainfall <= 175:
				rainfall2 = 0
			if rainfall < 145 or rainfall > 225:
				rainfall2 = -1
			
			if float(weather['temperature']) >= 21 and float(weather['temperature']) <=27:
				temperature2 = 1
			if float(weather['temperature']) < 21:
				temperature2 = -1
			if float(weather['temperature']) >27:
				temperature2 = -1
			
			if float(weather['humidity']) >= 80 :
				humidity2 = 1
			if float(weather['humidity']) < 80 and float(weather['humidity']) >= 70:
				humidity2 = 0
			if float(weather['humidity']) < 70:
				humidity2 = -1

			
			if float(request.form.get('ph-entry')) >= 6 and float(request.form.get('ph-entry'))<=7 :
				ph2 = 1
			if float(request.form.get('ph-entry')) < 6:
				ph2 = -10**(6 - float(request.form.get('ph-entry')))
			if float(request.form.get('ph-entry')) > 7:
				ph2 = -10**(float(request.form.get('ph-entry')) - 7)
    
			fertility = sum([rainfall2, temperature2, humidity2, ph2, float(request.form.get('nitrogen-entry')), float(request.form.get('phosphorus-entry')), float(request.form.get('potassium-entry'))])

			print(fertility)

			return redirect(url_for('prediction', crop = prediction, fertility = round(fertility, 2), pdata = pdata_text))

		else:
			return '<div> 404 </div> <div> no internet </div>'


	return render_template('home.html')


@app.route('/prediction', methods = [ 'GET' ])
def prediction():
    return render_template('prediction.html', crop = request.args.get('crop'), fertility = request.args.get('fertility'), pdata = request.args.get('pdata'))
	


if __name__ == '__main__':
	app.run(debug = True)