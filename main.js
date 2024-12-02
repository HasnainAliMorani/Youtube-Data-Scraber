// YouTube API Key
const API_KEY = 'AIzaSyCW4fZwrNkPVEk9MKU1IhLykg9oXQnk920';

// DOM Elements
const channelForm = document.getElementById('channel-form');
const channelInput = document.getElementById('channel-input');
const videoContainer = document.getElementById('video-container');
const channelData = document.getElementById('channel-data');

const defaultChannel = 'techguyweb';

// Form submit and fetch channel
channelForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const channel = channelInput.value.trim();
  if (!channel) {
    alert('Please enter a channel name!');
    return;
  }
  getChannel(channel);
});

// Get channel data using API key
function getChannel(channel) {
  fetch(
    `https://www.googleapis.com/youtube/v3/channels?part=snippet,contentDetails,statistics&forUsername=${channel}&key=${API_KEY}`
  )
    .then((response) => response.json())
    .then((data) => {
      if (data.items && data.items.length > 0) {
        const channel = data.items[0];

        const output = `
          <ul class="collection">
            <li class="collection-item">Title: ${channel.snippet.title}</li>
            <li class="collection-item">ID: ${channel.id}</li>
            <li class="collection-item">Subscribers: ${numberWithCommas(
              channel.statistics.subscriberCount
            )}</li>
            <li class="collection-item">Views: ${numberWithCommas(
              channel.statistics.viewCount
            )}</li>
            <li class="collection-item">Videos: ${numberWithCommas(
              channel.statistics.videoCount
            )}</li>
          </ul>
          <p>${channel.snippet.description}</p>
          <hr>
          <a class="btn grey darken-2" target="_blank" href="https://youtube.com/${
            channel.snippet.customUrl
          }">Visit Channel</a>
        `;
        showChannelData(output);

        const playlistId = channel.contentDetails.relatedPlaylists.uploads;
        requestVideoPlaylist(playlistId);
      } else {
        alert('Channel not found. Displaying default channel.');
        getChannel(defaultChannel);
      }
    })
    .catch((error) => {
      console.error('Error fetching channel:', error);
      alert('Failed to fetch channel. Please try again later.');
    });
}

// Add commas to numbers
function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Fetch videos from playlist
function requestVideoPlaylist(playlistId) {
  fetch(
    `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=${playlistId}&maxResults=10&key=${API_KEY}`
  )
    .then((response) => response.json())
    .then((data) => {
      const playListItems = data.items;

      if (playListItems && playListItems.length > 0) {
        let output = '<br><h4 class="center-align">Latest Videos</h4>';

        playListItems.forEach((item) => {
          const videoId = item.snippet.resourceId.videoId;

          output += `
            <div class="col s3">
              <iframe width="100%" height="auto" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
            </div>
          `;
        });

        videoContainer.innerHTML = output;
      } else {
        videoContainer.innerHTML = '<p>No Uploaded Videos</p>';
      }
    })
    .catch((error) => {
      console.error('Error fetching playlist videos:', error);
      videoContainer.innerHTML = '<p>Failed to load videos. Please try again later.</p>';
    });
}

// Display channel data
function showChannelData(data) {
  channelData.innerHTML = data;
}
