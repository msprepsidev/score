from flask import Flask, request, jsonify
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

sentiment_analyzer = SentimentIntensityAnalyzer()

profile_db = {}

def analyze_post_sentiment(post):
    score = sentiment_analyzer.polarity_scores(post['text'])['compound']
    return score

def update_likes_score(profile_id, new_likes):
    profile_data = profile_db.get(profile_id, {"like_score": 50, "total_likes": 0, "liked_posts": []})
    
    new_sentiment_scores = [analyze_post_sentiment(post) for post in new_likes]
    avg_new_score = np.mean(new_sentiment_scores) * 50 + 50  # Transformer [-1, 1] en [0, 100]

    total_likes = profile_data["total_likes"] + len(new_likes)
    
    old_score = profile_data["like_score"]
    weight_old = profile_data["total_likes"]
    weight_new = len(new_likes)

    updated_score = (old_score * weight_old + avg_new_score * weight_new) / total_likes
    
    profile_db[profile_id] = {
        "like_score": updated_score,
        "total_likes": total_likes,
        "liked_posts": profile_data["liked_posts"] + new_likes  # Ajouter les nouveaux posts likés à l'historique
    }

    return updated_score

@app.route('/profile/update_likes_score', methods=['POST'])
def update_likes_score():
    data = request.json
    profile_id = data.get('profile_id')

    if not profile_id:
        return jsonify({"error": "Profile ID is required"}), 400

    new_likes = data.get("new_likes", [])

    if not new_likes:
        return jsonify({"error": "No new liked posts provided"}), 400

    updated_score = update_likes_score(profile_id, new_likes)

    return jsonify({
        "profile_id": profile_id,
        "updated_likes_score": updated_score,
        "new_likes_analyzed": new_likes,
        "total_likes": profile_db[profile_id]["total_likes"]
    })

@app.route('/profile/get_likes_score', methods=['GET'])
def get_likes_score():
    profile_id = request.args.get('profile_id')

    if not profile_id or profile_id not in profile_db:
        return jsonify({"error": "Profile ID not found"}), 404

    profile_data = profile_db[profile_id]

    return jsonify({
        "profile_id": profile_id,
        "current_likes_score": profile_data["like_score"],
        "total_likes": profile_data["total_likes"],
        "liked_posts_history": profile_data["liked_posts"]
    })

if __name__ == '__main__':
    app.run(debug=True)
