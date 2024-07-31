from yt_dlp import YoutubeDL

def download_video(video_name, video_url, storage_path: str) -> str:
    ydl_opts = {
        # 'format': 'best',
        'outtmpl': f'{storage_path}/{video_name}.%(ext)s',
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        video_file = f"{video_name}.mp4"
        return video_file

    except Exception as e:
        print(f"Error descargando el video: {e}")
        return False