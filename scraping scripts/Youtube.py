import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Replace with your API Key
API_KEY = "AIzaSyA_dQNgfgchN2W3UB2vEPt1ZeE120QRO8g"

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to search for videos based on a query
def search_videos(query, max_results=10):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results
    )
    response = request.execute()
    video_ids = [item["id"]["videoId"] for item in response["items"]]
    return video_ids

# Function to get video details
def get_video_details(video_id):
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()

    if "items" in response and len(response["items"]) > 0:
        video = response["items"][0]
        return {
            "title": video["snippet"]["title"],
            "description": video["snippet"]["description"],
            "views": video["statistics"].get("viewCount", "N/A"),
            "likes": video["statistics"].get("likeCount", "N/A"),
            "published_date": video["snippet"]["publishedAt"]
        }
    return None

# Function to get comments from a video
def get_video_comments(video_id):
    comments = []
    next_page_token = None

    try:
        while True:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "author": comment["authorDisplayName"],
                    "comment": comment["textDisplay"],
                    "likes": comment["likeCount"],
                    "published_at": comment["publishedAt"]
                })

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
    except HttpError as e:
        if e.resp.status == 403 and "commentsDisabled" in str(e):
            print(f"Comments are disabled for video ID: {video_id}")
        else:
            print(f"An error occurred while fetching comments for video ID: {video_id}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for video ID: {video_id}: {e}")

    return comments

# Main function to fetch data for a query
def fetch_youtube_data(query):
    # Search for videos
    video_ids = search_videos(query)

    # Fetch data for each video
    youtube_data = []
    for video_id in video_ids:
        video_data = get_video_details(video_id)
        comments_data = get_video_comments(video_id)

        youtube_data.append({
            "video_details": video_data,
            "comments": comments_data
        })

    # Save to JSON file
    with open(f"{query}_youtube_data.json", "w", encoding="utf-8") as json_file:
        json.dump(youtube_data, json_file, indent=4, ensure_ascii=False)

    print(f"YouTube data saved successfully in '{query}_youtube_data.json'")

# Example usage
query = "president trump 2025"
fetch_youtube_data(query)
