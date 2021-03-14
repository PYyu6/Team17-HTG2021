'''
Created on Mar 13, 2021

@author: Josh
'''
import decimal
import pymysql as sql
import make_response
from flask import Flask, request, jsonify
app = Flask(__name__)

def sanitize_decimal(dtuple):
    dtuple = list(dtuple)
    for i in range(len(dtuple)):
        if type(dtuple[i]) == decimal.Decimal:
            dtuple[i] = float(dtuple[i])
    print(dtuple)
    return tuple(dtuple)

#purpose: gets best 3 institutions of x type
#params: type

@app.route('/webhook', methods=['POST'])
def respond():
    req = request.get_json(silent=True, force=True)
    query_result = req.get('queryResult')
    params = query_result.get("parameters")
    lastcontext = query_result.get('outputContexts')[0].get("parameters")
    response = ""
    
    if (query_result.get("action") == "writeShelter.writeShelter-fallback"):
        response = post_rating(lastcontext.get("sheltername"), None, query_result.get("queryText"));
    
    return {
      "fulfillmentMessages": [
        {
          "text": {
            "text": [
              response
            ]
          }
        }
      ]
    }
    
def get_best_institution_of_type (institution_type):
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    cursor.execute("SELECT institutions.name, AVG(ratings.rating) FROM institutions JOIN ratings ON institutions.id = ratings.institution_id WHERE type = '%s' AND ratings.rating IS NOT NULL GROUP BY institutions.name ORDER BY AVG(ratings.rating)" %(institution_type))
    return jsonify(sanitize_decimal(cursor.fetchone()))

#purpose: gets all institutions of x type
#params: type
def get_institutions_of_type(institution_type):
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM institutions WHERE type = '%s'" %(institution_type))
    return jsonify(cursor.fetchone())

#purpose: gets institution info based on name
#params: name
def get_institution(institution):
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM institutions WHERE name = '%s'" %(institution))
    return jsonify(cursor.fetchone())

#purpose: gives an institution a rating, or an initiative a rating, initiative takes priority
#params: rating, institution, initiative
def post_rating(institution_raw, initiative_raw, rating):
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    
    institution = None
    initiative = None
    
    if institution_raw:
        cursor.execute("SELECT id FROM institutions WHERE name = '%s'" %(institution_raw))
        institution = cursor.fetchone()[0]
    if initiative_raw:
        cursor.execute("SELECT id FROM initiatives WHERE name = '%s'" %(initiative_raw))
        initiative = cursor.fetchone()[0]
    
    # You can add the test cases you made in the previous function, but in our case here you are just testing the POST functionality
    if rating and (institution or initiative):
        if rating.isdigit() and int(rating) < 5:
            if initiative:
                query = "INSERT INTO ratings (institution_id, rating) VALUES (%s, %s)" %(institution, rating)
            else:
                query = "INSERT INTO ratings (initiative_id, rating) VALUES (%s, %s)" %(initiative, rating)
        else:
            if initiative:
                query = "INSERT INTO ratings (institution_id, review) VALUES (%s, '%s')" %(institution, rating)
            else:
                query = "INSERT INTO ratings (initiative_id, review) VALUES (%s, '%s')" %(initiative, rating)
             
        print(query)
        cursor.execute(query)
        conn.commit();
        return "Thanks for leaving a review"
    else:
        return "Sorry, this institution or initiative does not exist in our system"

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

def get_rating(institution_raw, initiative_raw, rating_type):
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    
    institution = None
    initiative = None
    res = None
    
    if not rating_type:
        return jsonify({
            "ERROR": "missing variable rating_type"
        })
    
    if institution_raw:
        cursor.execute("SELECT id FROM institutions WHERE name = '%s'" %(institution_raw))
        institution = cursor.fetchone()[0]
        if rating_type == 'rating':
            cursor.execute("SELECT AVG(rating) FROM ratings WHERE institution_id = %s AND rating IS NOT NULL" %(institution))
            res = cursor.fetchone()
            print(res)
            if res:
                return jsonify(sanitize_decimal(res))
            else:
                return jsonify({
                    "ERROR": "Sorry, this institution or initiative does not exist in our system"
                })
        else:
            cursor.execute("SELECT review FROM ratings WHERE institution_id = %s AND review IS NOT NULL ORDER BY id DESC LIMIT 3" %(institution))
            res = cursor.fetchone()
            if res:
                return jsonify(sanitize_decimal(res))
            else:
                return jsonify({
                    "ERROR": "Sorry, this institution or initiative does not exist in our system"
                })
    elif initiative_raw:
        cursor.execute("SELECT id FROM initiatives WHERE name = '%s'" %(initiative_raw))
        initiative = cursor.fetchone()[0]
        if rating_type == 'rating':
            cursor.execute("SELECT AVG(rating) FROM ratings WHERE initiative_id = %s AND rating IS NOT NULL" %(initiative))
            if res:
                return jsonify(sanitize_decimal(res))
            else:
                return jsonify({
                    "ERROR": "Sorry, this institution or initiative does not exist in our system"
                })
        else:
            cursor.execute("SELECT review FROM ratings WHERE initiative_id = %s AND review IS NOT NULL ORDER BY id DESC LIMIT 3" %(initiative))
            res = cursor.fetchone()
            if res:
                return jsonify(sanitize_decimal(res))
            else:
                return jsonify({
                    "ERROR": "Sorry, this institution or initiative does not exist in our system"
                })
    else:
        return jsonify({
            "ERROR": "Sorry, this institution or initiative does not exist in our system"
        })
    
    
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)