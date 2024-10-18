from flask import Flask, request, jsonify
import requests 

app = Flask(__name__)

POSTS_SCORE_URL = "http://127.0.0.1:5000/profile/get_posts_score"
LIKES_SCORE_URL = "http://127.0.0.1:5000/profile/get_likes_score"
COMMENTS_SCORE_URL = "http://127.0.0.1:5000/profile/get_comments_score"

def get_score_from_api(url, profile_id):
    try:
        response = requests.get(url, params={'profile_id': profile_id})
        if response.status_code == 200:
            data = response.json()
            return data.get('score') or data.get('current_posts_score') 
        else:
            return None
    except Exception as e:
        print(f"Error calling {url}: {str(e)}")
        return None

def calculate_average_score(profile_id):
    post_score = get_score_from_api(POSTS_SCORE_URL, profile_id)
    like_score = get_score_from_api(LIKES_SCORE_URL, profile_id)
    comment_score = get_score_from_api(COMMENTS_SCORE_URL, profile_id)

    if post_score is None or like_score is None or comment_score is None:
        return None  

    average_score = (post_score + like_score + comment_score) / 3
    return average_score

@app.route('/profile/get_average_score', methods=['GET'])
def get_average_score():
    profile_id = request.args.get('profile_id')

    if not profile_id:
        return jsonify({"error": "Profile ID is required"}), 400

    average_score = calculate_average_score(profile_id)

    if average_score is None:
        return jsonify({"error": "Profile not found or one of the scores couldn't be retrieved"}), 404

    return jsonify({
        "profile_id": profile_id,
        "average_score": average_score
    })

if __name__ == '__main__':
    app.run(debug=True)
