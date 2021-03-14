'''
Created on Mar 13, 2021

@author: Josh
'''
import decimal
import pymysql as sql
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
@app.route('/get_best_institution_of_type/', methods=['GET'])
def get_best_institution_of_type ():
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    institution_type = request.args.get("type")
    cursor.execute("SELECT institutions.name, AVG(ratings.rating) FROM institutions JOIN ratings ON institutions.id = ratings.institution_id WHERE type = '%s' AND ratings.rating IS NOT NULL GROUP BY institutions.name ORDER BY AVG(ratings.rating)" %(institution_type))
    return jsonify(sanitize_decimal(cursor.fetchone()))

#purpose: gets all institutions of x type
#params: type
@app.route('/get_institutions_of_type/', methods=['GET'])
def get_institutions_of_type():
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    institution_type = request.args.get("type")
    cursor.execute("SELECT * FROM institutions WHERE type = '%s'" %(institution_type))
    return jsonify(cursor.fetchone())

#purpose: gets institution info based on name
#params: name
@app.route('/get_institution/', methods=['GET'])
def get_institution():
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    
    institution = request.args.get("institution")
    cursor.execute("SELECT * FROM institutions WHERE name = '%s'" %(institution))
    return jsonify(cursor.fetchone())

#purpose: gives an institution a rating, or an initiative a rating, initiative takes priority
#params: rating, institution, initiative
@app.route('/post_rating/', methods=['GET'])
def post_rating():
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    
    institution_raw = request.args.get('institution')
    initiative_raw = request.args.get('initiative')
    institution = None
    initiative = None
    
    if institution_raw:
        cursor.execute("SELECT id FROM institutions WHERE name = '%s'" %(institution_raw))
        institution = cursor.fetchone()[0]
    if initiative_raw:
        cursor.execute("SELECT id FROM initiatives WHERE name = '%s'" %(initiative_raw))
        initiative = cursor.fetchone()[0]
    
    rating = request.args.get('rating')
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
        return jsonify(success=True)
    else:
        return jsonify({
            "ERROR": "missing crucial variable"
        })

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

@app.route('/get_rating/', methods=['GET'])
def get_rating():
    conn = sql.connect(
        host = "us-cdbr-east-03.cleardb.com",
        user = "bc15a20e969c5b",
        password = "938fc6aa",
        database = "heroku_133c8289fb09686"
        );
    cursor = conn.cursor()
    
    institution_raw = request.args.get('institution')
    initiative_raw = request.args.get('initiative')
    institution = None
    initiative = None
    res = None
    
    rating_type = request.args.get('rating_type')
    
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
                    "ERROR": "none found"
                })
        else:
            cursor.execute("SELECT review FROM ratings WHERE institution_id = %s AND review IS NOT NULL ORDER BY id DESC LIMIT 3" %(institution))
            res = cursor.fetchone()
            if res:
                return jsonify(sanitize_decimal(res))
            else:
                return jsonify({
                    "ERROR": "none found"
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
                    "ERROR": "none found"
                })
        else:
            cursor.execute("SELECT review FROM ratings WHERE initiative_id = %s AND review IS NOT NULL ORDER BY id DESC LIMIT 3" %(initiative))
            res = cursor.fetchone()
            if res:
                return jsonify(sanitize_decimal(res))
            else:
                return jsonify({
                    "ERROR": "none found"
                })
    else:
        return jsonify({
            "ERROR": "missing variable institution or initiative"
        })
    
    
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)