from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import processor

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/', methods=["GET", "POST"])
def index():
    return ""


@app.route('/chatbot', methods=["POST"],strict_slashes = False)
def chatbotResponse():

    if request.method == 'POST':
        the_question = request.json['question']
        print(the_question)

        response = processor.chatbot_response(the_question)

    return jsonify({"response": response })

@app.route('/chats')
def home():
    client = MongoClient("mongodb+srv://it21323966:it21323966@chatbot.nwchqbe.mongodb.net/")
    db = client["ecommerce"]
    mycol = db["products"]

    mylist = [
  { "product": "T-shirt", "price": "5000"},
  { "product": "shorts", "price": "3000"},
  { "product": "blouse", "price": "2000"},
  { "product": "socks", "price": "3000"},
]
    x = mycol.insert_many(mylist)
    
    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
