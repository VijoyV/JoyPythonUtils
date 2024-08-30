from youtube_transcript_api import YouTubeTranscriptApi
import os

def download_auto_generated_captions(video_id, output_path):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        output_file_path = os.path.join(output_path, f"{video_id}_captions.srt")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for i, line in enumerate(transcript):
                start = line['start']
                end = line['start'] + line['duration']
                text = line['text'].replace('\n', ' ').replace('\r', '')
                f.write(f"{i+1}\n{convert_to_srt_time(start)} --> {convert_to_srt_time(end)}\n{text}\n\n")
        print(f"Auto-generated captions downloaded for video {video_id}")
    except Exception as e:
        print(f"Failed to download auto-generated captions for video {video_id}: {e}")

def convert_to_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"



# Video ID of the YouTube video
video_id = "RBzXsQHjptQ"

# Output path where captions will be saved
output_path = "C:\\Users\\vijoy\\Downloads\\YouTubeVideos"

download_auto_generated_captions(video_id, output_path)
