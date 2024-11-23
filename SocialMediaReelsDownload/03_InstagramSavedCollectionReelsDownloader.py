import instaloader
import os


def download_reels_from_collection(username, password, collection_name, download_folder):
    try:
        # Create an instance of Instaloader with video-only settings
        loader = instaloader.Instaloader(download_pictures=False,
                                         download_video_thumbnails=False,
                                         download_geotags=False,
                                         save_metadata=False)

        # Login to Instagram
        print("Logging in...")
        loader.login(username, password)

        # Fetch all collections
        print("Fetching collections...")
        collections = loader.context.graphql_query(
            "query ($id: ID!, $first: Int) {"
            "  user(id: $id) {"
            "    saved_collections(first: $first) {"
            "      edges {"
            "        node {"
            "          id"
            "          name"
            "          posts {"
            "            count"
            "          }"
            "        }"
            "      }"
            "    }"
            "  }"
            "}",
            {"id": loader.context.user_id, "first": 50}
        )["data"]["user"]["saved_collections"]["edges"]

        # Find the collection matching the specified name
        collection_id = None
        for collection in collections:
            if collection["node"]["name"] == collection_name:
                collection_id = collection["node"]["id"]
                print(f"Found collection '{collection_name}' with ID {collection_id}")
                break

        if not collection_id:
            print(f"Collection '{collection_name}' not found.")
            return

        # Create the download folder if it doesn't exist
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Fetch posts from the specified collection
        print(f"Fetching posts from collection '{collection_name}'...")
        posts = loader.context.graphql_query(
            "query ($id: ID!, $first: Int) {"
            "  collection(id: $id) {"
            "    posts(first: $first) {"
            "      edges {"
            "        node {"
            "          shortcode"
            "          __typename"
            "          video_url"
            "        }"
            "      }"
            "    }"
            "  }"
            "}",
            {"id": collection_id, "first": 100}
        )["data"]["collection"]["posts"]["edges"]

        # Download only Reels (GraphVideo) from the collection
        print("Downloading Reels...")
        reel_count = 0
        for post in posts:
            if post["node"]["__typename"] == "GraphVideo":  # Check if it's a Reel
                shortcode = post["node"]["shortcode"]
                video_url = post["node"]["video_url"]
                video_path = os.path.join(download_folder, f"{shortcode}.mp4")

                # Download the video
                response = loader.context.session.get(video_url, stream=True)
                with open(video_path, "wb") as video_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            video_file.write(chunk)

                print(f"Downloaded Reel: {shortcode}.mp4")
                reel_count += 1

        print(f"Downloaded {reel_count} Reels from collection '{collection_name}' to '{download_folder}'.")
    except instaloader.exceptions.LoginRequiredException:
        print("Login failed. Please check your username and password.")
    except Exception as e:
        print(f"Error: {e}")


# Usage example
username = 'vijoyvallachira'
password = 'Sona$Kutty'
collection_name = 'Beauties'

# username = input("Enter your Instagram username: ")
# password = input("Enter your Instagram password: ")
# collection_name = input("Enter the name of the collection to download Reels from: ")
download_folder = "saved_reels_beauties"  # Change the folder as needed
download_reels_from_collection(username, password, collection_name, download_folder)
