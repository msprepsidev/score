
from flask import Flask, request, jsonify
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

sentiment_analyzer = SentimentIntensityAnalyzer()

profile_db = {}

def analyze_comment_sentiment(comment):
    score = sentiment_analyzer.polarity_scores(comment['text'])['compound']
    return score

def calculate_comment_score(comments):
    sentiment_scores = [analyze_comment_sentiment(comment) for comment in comments]
    avg_score = np.mean(sentiment_scores) * 50 + 50 
    return max(1, min(100, avg_score)) 

def update_comment_score(profile_id, new_comments):
    profile_data = profile_db.get(profile_id, {"comment_score": 50, "total_comments": 0, "comments": []})
    
    new_sentiment_scores = [analyze_comment_sentiment(comment) for comment in new_comments]
    avg_new_score = np.mean(new_sentiment_scores) * 50 + 50  

    total_comments = profile_data["total_comments"] + len(new_comments)
    
    old_score = profile_data["comment_score"]
    weight_old = profile_data["total_comments"]
    weight_new = len(new_comments)

    updated_score = (old_score * weight_old + avg_new_score * weight_new) / total_comments
    
    profile_db[profile_id] = {
        "comment_score": updated_score,
        "total_comments": total_comments,
        "comments": profile_data["comments"] + new_comments  
    }

    return updated_score

@app.route('/profile/update_comments_score', methods=['POST'])
def update_comments_score():
    data = request.json
    profile_id = data.get('profile_id')

    if not profile_id:
        return jsonify({"error": "Profile ID is required"}), 400

    new_comments = data.get("new_comments", [])

    if not new_comments:
        return jsonify({"error": "No new comments provided"}), 400

    updated_score = update_comment_score(profile_id, new_comments)

    return jsonify({
        "profile_id": profile_id,
        "updated_comments_score": updated_score,
        "new_comments_analyzed": new_comments,
        "total_comments": profile_db[profile_id]["total_comments"]
    })

@app.route('/profile/get_comments_score', methods=['GET'])
def get_comments_score():
    profile_id = request.args.get('profile_id')

    if not profile_id or profile_id not in profile_db:
        return jsonify({"error": "Profile ID not found"}), 404

    profile_data = profile_db[profile_id]

    return jsonify({
        "profile_id": profile_id,
        "current_comments_score": profile_data["comment_score"],
        "total_comments": profile_data["total_comments"],
        "comments_history": profile_data["comments"]
    })

if __name__ == '__main__':
    app.run(debug=True)
