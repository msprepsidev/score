from flask import Flask, request, jsonify
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

sentiment_analyzer = SentimentIntensityAnalyzer()

profile_db = {}

def analyze_post_sentiment(post):
    score = sentiment_analyzer.polarity_scores(post['text'])['compound']
    return score

def update_posts_score(profile_id, new_posts):
    profile_data = profile_db.get(profile_id, {"post_score": 50, "total_posts": 0, "posted_content": []})
    
    new_sentiment_scores = [analyze_post_sentiment(post) for post in new_posts]
    avg_new_score = np.mean(new_sentiment_scores) * 50 + 50  

    total_posts = profile_data["total_posts"] + len(new_posts)
    
    old_score = profile_data["post_score"]
    weight_old = profile_data["total_posts"]
    weight_new = len(new_posts)

    updated_score = (old_score * weight_old + avg_new_score * weight_new) / total_posts
    
    profile_db[profile_id] = {
        "post_score": updated_score,
        "total_posts": total_posts,
        "posted_content": profile_data["posted_content"] + new_posts 
    }

    return updated_score

@app.route('/profile/update_posts_score', methods=['POST'])
def update_posts_score():
    data = request.json
    profile_id = data.get('profile_id')

    if not profile_id:
        return jsonify({"error": "Profile ID is required"}), 400

    new_posts = data.get("new_posts", [])

    if not new_posts:
        return jsonify({"error": "No new posts provided"}), 400

    updated_score = update_posts_score(profile_id, new_posts)

    return jsonify({
        "profile_id": profile_id,
        "updated_posts_score": updated_score,
        "new_posts_analyzed": new_posts,
        "total_posts": profile_db[profile_id]["total_posts"]
    })

@app.route('/profile/get_posts_score', methods=['GET'])
def get_posts_score():
    profile_id = request.args.get('profile_id')

    if not profile_id or profile_id not in profile_db:
        return jsonify({"error": "Profile ID not found"}), 404

    profile_data = profile_db[profile_id]

    return jsonify({
        "profile_id": profile_id,
        "current_posts_score": profile_data["post_score"],
        "total_posts": profile_data["total_posts"],
        "posted_content_history": profile_data["posted_content"]
    })

if __name__ == '__main__':
    app.run(debug=True)
