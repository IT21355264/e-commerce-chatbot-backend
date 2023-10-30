import nltk
import json
import random
import pickle
import numpy as np
import re
from pymongo import MongoClient
from keras.models import load_model
from nltk.stem import WordNetLemmatizer


model = load_model('chatbot_model.h5')
intents = json.loads(open('intents.json', encoding='utf-8').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
client = MongoClient("mongodb+srv://it21323966:it21323966@chatbot.nwchqbe.mongodb.net/")
db = client["ecommerce"]

lemmatizer = WordNetLemmatizer()


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(msg,ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']

    mycol = db["products"]

    result = "return I'm sorry, I don't understand that."

    for i in list_of_intents:
        if(i['tag']== tag):

            if tag == 'products':

                result = "We sell "
                results = mycol.find({})
                
                for doc in results:
                    result += doc['product'] + " "
                
                return result

            elif tag == "track":
                order_id = extract_order_id(msg)  # Implement this function

                if order_id:
                    order_status, result = getOrderStatus(order_id)
                else:
                    result = "Please provide me with order details"

                return result

            elif tag == 'track_id':
                order_status, result = getOrderStatus(int(the_question))

                return result
            
            elif tag == "brands":
                item, brands = extract_brand(msg)

                result = item + ": "

                for brand in brands:
                    result += brand + " "
                
                return result

            else:
                result = random.choice(i['responses'])
                break
        
        
            
    return result

def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(msg, ints, intents)
    return res


def getOrderStatus(order_id):
    # try:  
    #     print(order_id)
    collection = db["orders"]
    order = collection.find_one({"order_id": int(order_id)})
    #     return order['status']
    # except Exception as e:
    #     print('Error: ', e)
    if order:
        order_status = order.get("status", "Status not available")
        # print("Order Status:", order_status)
        response = f"Order Status is: {order_status}\nPlease contact us for further information"
        return(order_status, response)
    else:
        print("Order not found.")

def extract_order_id(user_input):
    order_id = None
    pattern = r"(\d+)"
    match = re.search(pattern, user_input)
    if match:
        order_id = match.group(1)
    return order_id

def extract_brand(user_input):
    item_pattern = ["T-shirts", "Trousers"]
    mycol = db["products"]

    user_input = user_input.lower()

    for item in item_pattern:

        match = re.search(item.lower(), user_input)

        if match:
            brands = mycol.find({"product": item})
            
            for b in brands:
                return item, b['brand']
    
    

