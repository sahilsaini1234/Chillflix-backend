from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from numpy import random
import requests
import os
import random
from datetime import date
data = pd.read_csv('file1.csv')
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/movielist")
def get_movie_list():
    d = list(set(list(data['title'].values)))
    if(len(d) == 0):
        return jsonify(None)
    return jsonify(d)

@app.route("/search/<string:moviename>")
def get_movie(moviename):
    url = f"https://api.themoviedb.org/3/search/movie?api_key=b0c85734cc066c72c35a39b2b47b775e&language=en-US&page=1&include_adult=false&query={moviename}"
    response = requests.get(url)
    data = response.json()
    l=[]
    for i in data['results']:
        if(i['release_date']>str(date.today())):
            continue
        d={}
        d['title']=i['original_title'];
        d['id']=i['id']
        d['poster_path']=i['poster_path']
        l.append(d)
        if(len(l)==10):
         break
    return jsonify(l)

@app.route("/getids/<string:moviename>")
def get_ids(moviename):
    m_data = data[data['title'].str.lower()==moviename.lower()] 
    if(len(m_data)==0):
         x = random.randint(0,3000)
         tmdb_id=str(data.loc[x].id)
    else:
        tmdb_id=str(m_data['id'].values[0])  
    re = requests.get('https://api.themoviedb.org/3/movie/'+tmdb_id+'?api_key=b0c85734cc066c72c35a39b2b47b775e&language=en-US')
    imdb_id= -1
    res = re.json()
    imdb_id = str(res['imdb_id'])
    result = {'imdb_id':imdb_id,'tmdb_id':tmdb_id}
    return jsonify(result)

@app.route("/similarity/<string:imdb_id>")
def get_movie_similarity(imdb_id):
    v = TfidfVectorizer(max_features=5000,stop_words='english')
    vectors= v.fit_transform(data['final'])
    similarity = cosine_similarity(vectors)
    l = []
    m_data=data[data['id']==imdb_id]
    if(len(m_data)==0):
         x = random.randint(0,3000)
         temp1=data.loc[x,:]
         movie = temp1['title']
    else:
        temp1=m_data['id']
        movie = temp1['title'].values[0]
    temp2 = data[data['title'] == movie]
    idx = temp2.index[0]
    dis = sorted(list(enumerate(similarity[idx])), reverse=True, key=(lambda x: x[1]))[1:11]
    for i in dis:
        a=str(data['id'][i[0]])
        re = requests.get('https://api.themoviedb.org/3/movie/'+a+'?api_key=b0c85734cc066c72c35a39b2b47b775e&language=en-US')
        v = re.json()
        l.append({'title':data['title'][i[0]],'id':int(data['id'][i[0]]),'movie_detail':v})
    return jsonify(l)


if __name__ == "__main__":
    app.run(debug=True)
 # type: ignore
