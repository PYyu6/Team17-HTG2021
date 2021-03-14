'''
Created on Mar 13, 2021

@author: Josh
'''
import pymysql as sql
from flask import Flask, request, jsonify
app = Flask(__name__)

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
            if institution:
                query = "INSERT INTO ratings (institution_id, rating) VALUES (%s, %s)" %(institution, rating)
            else:
                query = "INSERT INTO ratings (initiative_id, rating) VALUES (%s, %s)" %(initiative, rating)
        else:
            if institution:
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
            return str(cursor.fetchone()[0])
        else:
            cursor.execute("SELECT review FROM ratings WHERE institution_id = %s AND review IS NOT NULL ORDER BY id DESC LIMIT 3" %(institution))
            return cursor.fetchone()[0]
    elif initiative_raw:
        cursor.execute("SELECT id FROM initiatives WHERE name = '%s'" %(initiative_raw))
        initiative = cursor.fetchone()[0]
        if rating_type == 'rating':
            cursor.execute("SELECT AVG(rating) FROM ratings WHERE initiative_id = %s AND rating IS NOT NULL" %(initiative))
            return str(cursor.fetchone()[0])
        else:
            cursor.execute("SELECT review FROM ratings WHERE initiative_id = %s AND review IS NOT NULL ORDER BY id DESC LIMIT 3" %(initiative))
            return cursor.fetchone()[0]
    else:
        return jsonify({
            "ERROR": "missing variable institution or initiative"
        })
    
    
if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)