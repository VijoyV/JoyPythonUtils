import instaloader


def download_instagram_reel(username, reel_shortcode, download_folder):
    try:
        # Create an instance of Instaloader
        loader = instaloader.Instaloader(download_pictures=False, download_video_thumbnails=False)

        # Login to Instagram (optional but required for private accounts)
        # loader.login(username, password)  # Uncomment and replace with credentials if needed

        # Download Reel using its shortcode
        reel_url = f"https://www.instagram.com/reel/{reel_shortcode}/"
        loader.download_post(instaloader.Post.from_shortcode(loader.context, reel_shortcode), target=download_folder)

        print(f"Reel downloaded successfully in '{download_folder}'")
    except Exception as e:
        print(f"Error downloading reel: {e}")


# Usage example
username = "vijoyvallachira"  # Optional if login is required
reel_shortcode = "DCeRmqeSqXD"  # Extract from the Reel's URL
download_folder = "reels"
download_instagram_reel(username, reel_shortcode, download_folder)

"""
    1. https://www.instagram.com/reel/DCeRmqeSqXD/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==

"""