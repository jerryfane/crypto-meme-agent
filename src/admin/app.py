import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify
from models.db_wrapper import DBWrapper

app = Flask(__name__)
db = DBWrapper()

@app.route('/')
def index():
    status = request.args.get('status', 'review')
    context = request.args.get('context', None)
    
    # Get stats, contexts, and filtered tweets
    stats = db.get_tweets_stats()
    contexts = db.get_contexts()
    tweets = db.get_tweets_filtered(status=status, context=context)
    
    return render_template('review.html', 
                         tweets=tweets,
                         stats=stats,
                         contexts=contexts,
                         current_status=status,
                         current_context=context)

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