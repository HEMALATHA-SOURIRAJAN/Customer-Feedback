from flask import Flask, render_template, url_for,redirect, request 
from flask_mysqldb import MySQL
import nltk  
import re, string
from nltk.corpus import twitter_samples
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import FreqDist
import random
from nltk import classify
from nltk import NaiveBayesClassifier
from nltk.tokenize import word_tokenize
app = Flask(__name__,static_url_path='/static')
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/brand')
def brand():
    return render_template('brand.html')
@app.route('/special')
def special():
    return render_template('special.html')
@app.route('/contact')   
def contact():
    return render_template('contact.html')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hemeu05'
app.config['MYSQL_DB'] = 'datadb'
@app.route('/senti', methods=['GET','POST'])
def senti():
    if request.method == 'POST':
        User_name = request.form['User_name']
        Email_ID = request.form['Email_ID']
        Phone_Number = request.form['Phone_Number']
        Feedback= request.form['Feedback']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO consumer( User_name,Email_ID,Phone_Number,Feedback) VALUES (%s, %s,%s,%s)", ( User_name,Email_ID,Phone_Number,Feedback))
        mysql.connection.commit()
        #flash('Added successfully')
        cur.close()
        # cur.execute()
        print(User_name,Email_ID,Phone_Number,Feedback)
    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')
    text = twitter_samples.strings('tweets.20150430-223406.json')
    tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    def lemmatize_sentence(tokens):
        lemmatizer = WordNetLemmatizer()
        lemmatized_sentence = []
        for word, tag in pos_tag(tokens):
            if tag.startswith('NN'):
                 pos = 'n'
            elif tag.startswith('VB'):
                 pos = 'v'
            else:
                pos = 'a'
            lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
        return lemmatized_sentence
    def remove_noise(tweet_tokens, stop_words = ()):
        cleaned_tokens = []
        for token, tag in pos_tag(tweet_tokens):
            token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                        '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
            token = re.sub("(@[A-Za-z0-9_]+)","", token)
            if tag.startswith("NN"):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'
            lemmatizer = WordNetLemmatizer()
            token = lemmatizer.lemmatize(token, pos)
            if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())
        return cleaned_tokens
    stop_words = stopwords.words('english')
    positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')
    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []
    for tokens in positive_tweet_tokens:
         positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))
    for tokens in negative_tweet_tokens:
         negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))
    def get_all_words(cleaned_tokens_list):
        for tokens in cleaned_tokens_list:
            for token in tokens:
                 yield token
    all_pos_words = get_all_words(positive_cleaned_tokens_list)
    freq_dist_pos = FreqDist(all_pos_words)
    def get_tweets_for_model(cleaned_tokens_list):
         for tweet_tokens in cleaned_tokens_list:
            yield dict([token, True] for token in tweet_tokens)
    positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
    negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)
    positive_dataset = [(tweet_dict, "Positive")
                         for tweet_dict in positive_tokens_for_model]
    negative_dataset = [(tweet_dict, "Negative")
                         for tweet_dict in negative_tokens_for_model]
    dataset = positive_dataset + negative_dataset
    random.shuffle(dataset)
    train_data = dataset[:7000]
    test_data = dataset[7000:]
    classifier = NaiveBayesClassifier.train(train_data)
    custom_tweet = Feedback
    custom_tokens = remove_noise(word_tokenize(custom_tweet))
    ans=classifier.classify(dict([token, True] for token in custom_tokens))
    return render_template('contact.html',ans=ans)


mysql = MySQL(app)
@app.route('/')
def index():
  cur=mysql.connection.cursor()
  cur.execute('SELECT * FROM consumer')
  data=cur.fetchcall()
  cur.close()
  return render_template('index.html',contact=data)

   
@app.route('/',methods=['POST'])
def data():
   if request.method=="POST":
      return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)