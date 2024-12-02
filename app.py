from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# YouTube Data API Key
API_KEY = "AIzaSyCW4fZwrNkPVEk9MKU1IhLykg9oXQnk920"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

# HTML Template (Frontend)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YouTube Channel Data</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0-rc.2/css/materialize.min.css">
  <style>
    body {
      font-family: Arial, sans-serif;
    }
    nav {
      background-color: #000;
    }
    .container {
      margin-top: 20px;
    }
    iframe {
      border-radius: 5px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    }
  </style>
</head>
<body>
  <nav>
    <div class="nav-wrapper">
      <div class="container">
        <a href="#" class="brand-logo">YouTube Channel Data</a>
      </div>
    </div>
  </nav>

  <div class="container">
    <h5>Enter a YouTube Channel Name</h5>
    <form id="channel-form">
      <div class="input-field">
        <input type="text" id="channel-input" placeholder="Enter Channel Name" required>
      </div>
      <button type="submit" class="btn grey">Get Channel Data</button>
    </form>
    <div id="channel-data" class="section"></div>
    <div id="video-container" class="row"></div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0-rc.2/js/materialize.min.js"></script>
  <script>
    document.getElementById('channel-form').addEventListener('submit', async function (e) {
      e.preventDefault();
      const channelName = document.getElementById('channel-input').value;
      
      const response = await fetch(`/get_channel_data?channel=${encodeURIComponent(channelName)}`);
      const data = await response.json();

      if (data.error) {
        document.getElementById('channel-data').innerHTML = `<p style="color: red;">${data.error}</p>`;
        return;
      }

      // Display Channel Info
      const channelInfo = `
        <h6>Channel Info:</h6>
        <p><strong>Title:</strong> ${data.title}</p>
        <p><strong>Description:</strong> ${data.description}</p>
        <p><strong>Subscribers:</strong> ${data.subscribers}</p>
        <p><strong>Views:</strong> ${data.views}</p>
        <p><strong>Videos:</strong> ${data.videos}</p>
        <a class="btn blue" href="${data.url}" target="_blank">Visit Channel</a>
      `;
      document.getElementById('channel-data').innerHTML = channelInfo;

      // Display Videos
      const videos = data.videosList;
      const videoContainer = document.getElementById('video-container');
      videoContainer.innerHTML = '<h6>Latest Videos:</h6>';
      videos.forEach(video => {
        videoContainer.innerHTML += `
          <div class="col s4">
            <iframe width="100%" height="200" src="https://www.youtube.com/embed/${video.id}" frameborder="0" allowfullscreen></iframe>
            <p>${video.title}</p>
          </div>
        `;
      });
    });
  </script>
</body>
</html>
"""

# Serve HTML Frontend
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Backend API Endpoint
@app.route('/get_channel_data')
def get_channel_data():
    channel_name = request.args.get('channel')
    if not channel_name:
        return jsonify({"error": "Channel name is required"}), 400

    # Fetch channel details
    channel_url = f"{YOUTUBE_API_URL}/channels?part=snippet,statistics,contentDetails&forUsername={channel_name}&key={API_KEY}"
    channel_response = requests.get(channel_url).json()

    if "items" not in channel_response or not channel_response["items"]:
        return jsonify({"error": "Channel not found"}), 404

    channel_data = channel_response["items"][0]
    snippet = channel_data["snippet"]
    statistics = channel_data["statistics"]
    uploads_playlist_id = channel_data["contentDetails"]["relatedPlaylists"]["uploads"]

    # Fetch videos
    videos_url = f"{YOUTUBE_API_URL}/playlistItems?part=snippet&playlistId={uploads_playlist_id}&maxResults=5&key={API_KEY}"
    videos_response = requests.get(videos_url).json()

    videos_list = [
        {
            "id": video["snippet"]["resourceId"]["videoId"],
            "title": video["snippet"]["title"]
        } for video in videos_response.get("items", [])
    ]

    # Construct response
    response = {
        "title": snippet["title"],
        "description": snippet["description"],
        "subscribers": statistics.get("subscriberCount", "N/A"),
        "views": statistics.get("viewCount", "N/A"),
        "videos": statistics.get("videoCount", "N/A"),
        "url": f"https://www.youtube.com/channel/{channel_data['id']}",
        "videosList": videos_list
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
