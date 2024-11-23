import instaloader
import os
import re

def sanitize_filename(filename):
    """
    Remove invalid characters from filename for compatibility with filesystems.
    """
    return re.sub(r'[<>:"/\\|?*\']', '', filename).strip()

def download_saved_reels(username, password, download_folder):
    try:
        # Create an instance of Instaloader with video-only settings
        loader = instaloader.Instaloader(download_pictures=False,
                                         download_video_thumbnails=False,
                                         save_metadata=False)

        # Login to Instagram
        print("Logging in...")
        loader.login(username, password)

        # Fetch saved posts (including Reels saved from others)
        print("Fetching saved posts...")
        profile = instaloader.Profile.from_username(loader.context, username)
        saved_posts = profile.get_saved_posts()

        # Create the download folder if it doesn't exist
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Filter and download Reels
        print("Downloading saved Reels...")
        reel_count = 0
        for post in saved_posts:
            if post.typename == "GraphVideo" and post.is_video:  # Check if it's a Reel
                video_url = post.video_url
                shortcode = post.shortcode

                # Use caption as filename or fallback to shortcode
                caption = post.caption if post.caption else f"Reel_{shortcode}"
                filename = sanitize_filename(caption[:50])  # Limit filename length
                video_path = os.path.join(download_folder, f"{filename}.mp4")

                # Download the video
                response = loader.context.session.get(video_url, stream=True)
                with open(video_path, "wb") as video_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            video_file.write(chunk)

                print(f"Downloaded Reel: {filename}.mp4")
                reel_count += 1

        print(f"Downloaded {reel_count} saved Reels to '{download_folder}'.")
    except instaloader.exceptions.LoginRequiredException:
        print("Login failed. Please check your username and password.")
    except Exception as e:
        print(f"Error: {e}")

# Usage example

username = 'vijoyvallachira'
password = 'Sona$Kutty'

# username = input("Enter your Instagram username: ")
# password = input("Enter your Instagram password: ")
download_folder = "all_reels"  # Change the folder as needed
download_saved_reels(username, password, download_folder)




