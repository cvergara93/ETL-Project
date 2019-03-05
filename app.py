from flask import Flask, render_template, jsonify, redirect, request
import pymongo
from flask_pymongo import PyMongo
import ETL_Project_ScrapeNFL as sNFL

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/NFL_data"
mongo = PyMongo(app)

@app.route("/")
def index():
    try:
        NFL_data = mongo.db.NFL_data.find_one()
        return render_template('index.html', NFL_data=NFL_data)
    except:
        return redirect('http://localhost:5000/scrape', code=302)    

@app.route("/scrape")
def scrape():
    NFL_data = mongo.db.NFL_data
    # Run the scrape funtion
    NFL_data_scrape = sNFL.scrape()
    NFL_data.update(
        {},
        NFL_data_scrape,
        upsert=True
    )
    return redirect('http://localhost:5000/', code=302)

@app.route('/shutdown')
def shutdown_server():
    func = request.environ.get('server.shutdown')    
    if func is None:
        raise RuntimeError('Not running with the Server')
    func()
    return 'Shutting down Flask server...'    
    
if __name__ == "__main__":
    app.run(debug=True)
