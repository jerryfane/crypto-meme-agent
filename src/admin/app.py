from flask import Flask, render_template, request, jsonify
from models.db_wrapper import DBWrapper

app = Flask(__name__)
db = DBWrapper()

@app.route('/')
def index():
    tweets = db.get_tweets_for_review()
    return render_template('review.html', tweets=tweets)

@app.route('/api/tweets/<int:tweet_id>', methods=['POST'])
def update_tweet(tweet_id):
    data = request.json
    status = data.get('status')
    text_adjusted = data.get('text_adjusted')
    score = data.get('score')
    
    success = db.update_tweet_status(
        tweet_id=tweet_id,
        status=status,
        text_adjusted=text_adjusted,
        score=score
    )
    
    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(debug=True)