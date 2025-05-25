#!/usr/bin/env python3
import json
import os
import argparse
import urllib.request
import urllib.parse
import urllib.error
import random
import string
from typing import List, Dict, Optional

class MaveDigitalUploader:
    def __init__(self):
        self.base_url = "https://api.mave.digital/v1"
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36')
        ]

    def login(self, email: str, password: str) -> Dict:
        """Login to mave.digital and get access token"""
        url = f"{self.base_url}/auth/login"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        data = {
            'email': email,
            'password': password
        }

        request = urllib.request.Request(url, method='POST')
        for key, value in headers.items():
            request.add_header(key, value)

        request.data = json.dumps(data).encode('utf-8')

        try:
            response = self.opener.open(request)
            response_data = json.loads(response.read().decode('utf-8'))

            self.access_token = response_data.get('access_token')
            self.refresh_token = response_data.get('refresh_token')
            self.user_id = response_data.get('user', {}).get('id')

            print(f"Login successful for user: {response_data.get('user', {}).get('name')}")
            return response_data

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            raise Exception(f"Login failed: {e.code} - {error_message}")

    def upload_audio(self, podcast_id: str, audio_file_path: str) -> str:
        """Upload audio file to mave.digital"""
        if not self.access_token:
            raise Exception("Not logged in. Call login() first.")

        url = f"{self.base_url}/episodes/upload-audio"
        boundary = '----WebKitFormBoundary' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

        with open(audio_file_path, 'rb') as f:
            file_data = f.read()

        body = []
        body.append(f'--{boundary}'.encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="audio"; filename="{os.path.basename(audio_file_path)}"'.encode('utf-8'))
        body.append(b'Content-Type: audio/mpeg')
        body.append(b'')
        body.append(file_data)

        body.append(f'--{boundary}'.encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="podcast_id"'.encode('utf-8'))
        body.append(b'')
        body.append(podcast_id.encode('utf-8'))

        body.append(f'--{boundary}--'.encode('utf-8'))
        multipart_data = b'\r\n'.join(body)

        request = urllib.request.Request(url, method='POST')
        request.add_header('Authorization', f'Bearer {self.access_token}')
        request.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        request.data = multipart_data

        try:
            response = self.opener.open(request)
            response_data = json.loads(response.read().decode('utf-8'))

            episode_id = response_data.get('episode_id')
            print(f"Audio '{os.path.basename(audio_file_path)}' uploaded successfully. Episode ID: {episode_id}")

            self._wait_for_audio_processing(episode_id)
            return episode_id

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            raise Exception(f"Upload failed for {audio_file_path}: {e.code} - {error_message}")

    def upload_multiple_audios(self, podcast_id: str, audio_files: List[str]) -> List[str]:
        """Upload multiple audio files to mave.digital"""
        episode_ids = []
        for audio_file in audio_files:
            try:
                episode_id = self.upload_audio(podcast_id, audio_file)
                episode_ids.append(episode_id)
            except Exception as e:
                print(f"Failed to upload {audio_file}: {str(e)}")
                continue
        return episode_ids

    def _wait_for_audio_processing(self, episode_id: str, max_attempts: int = 30) -> bool:
        """Wait for audio processing to complete by polling the audio-status endpoint"""
        url = f"{self.base_url}/episodes/{episode_id}/audio-status"
        print("Waiting for audio processing to complete...")

        delay_seconds = 2  # Initial delay between polling attempts

        for attempt in range(max_attempts):
            try:
                request = urllib.request.Request(url, method='GET')
                request.add_header('Authorization', f'Bearer {self.access_token}')
                request.add_header('Accept', 'application/json')

                response = self.opener.open(request)
                response_data = json.loads(response.read().decode('utf-8'))

                audio_status = response_data.get('audio_status')

                if audio_status == 'success':
                    print(f"Audio processing completed successfully. Duration: {response_data.get('duration')} seconds")
                    return True
                elif audio_status == 'error':
                    raise Exception("Audio processing failed")
                else:
                    print(f"Audio processing in progress... (attempt {attempt + 1}/{max_attempts})")

            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f"Audio status not found yet, retrying... (attempt {attempt + 1}/{max_attempts})")
                else:
                    error_message = e.read().decode('utf-8')
                    print(f"Error checking audio status: {e.code} - {error_message}")

            import time
            time.sleep(min(delay_seconds * (1.5 ** attempt), 10))

        raise Exception(f"Audio processing timed out after {max_attempts} attempts")

    def publish_episode(self, episode_id: str, title: str, description: str, 
                       is_explicit: bool = False, is_private: bool = False, 
                       season: int = 1, number: int = 1) -> bool:
        """Publish an episode on mave.digital"""
        if not self.access_token:
            raise Exception("Not logged in. Call login() first.")

        url = f"{self.base_url}/episodes/{episode_id}/publish"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        data = {
            'title': title,
            'description': description,
            'type': 'full',
            'season': season,
            'number': number,
            'is_explicit': is_explicit,
            'is_optimize_bitrate': True,
            'is_private': is_private,
            'plans': []
        }

        request = urllib.request.Request(url, method='POST')
        for key, value in headers.items():
            request.add_header(key, value)

        request.data = json.dumps(data).encode('utf-8')

        try:
            response = self.opener.open(request)
            print(f"Episode '{title}' published successfully!")
            return True

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            raise Exception(f"Publishing failed: {e.code} - {error_message}")

    def publish_multiple_episodes(self, episodes_data: List[Dict]) -> bool:
        """Publish multiple episodes on mave.digital"""
        success = True
        for episode in episodes_data:
            try:
                self.publish_episode(
                    episode_id=episode['episode_id'],
                    title=episode['title'],
                    description=episode['description'],
                    is_explicit=episode.get('is_explicit', False),
                    is_private=episode.get('is_private', False),
                    season=episode.get('season', 1),
                    number=episode.get('number', 1)
                )
            except Exception as e:
                print(f"Failed to publish episode {episode.get('title')}: {str(e)}")
                success = False
                continue
        return success


def process_episodes_from_csv(csv_file: str) -> List[Dict]:
    """Helper function to process episode data from CSV file"""
    import csv
    episodes = []
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            episodes.append({
                'audio_file': row['audio_file'],
                'title': row['title'],
                'description': row['description'],
                'season': int(row.get('season', 1)),
                'number': int(row.get('number', 1)),
                'is_explicit': row.get('is_explicit', 'false').lower() == 'true',
                'is_private': row.get('is_private', 'false').lower() == 'true'
            })
    return episodes


def main():
    parser = argparse.ArgumentParser(description='Upload podcasts to mave.digital')
    
    # Single episode mode
    parser.add_argument('--email', required=True, help='Your mave.digital email')
    parser.add_argument('--password', required=True, help='Your mave.digital password')
    parser.add_argument('--podcast-id', required=True, help='ID of the podcast to upload to')
    
    # Options for single file upload
    parser.add_argument('--audio-file', help='Path to the audio file to upload (single file mode)')
    parser.add_argument('--title', help='Episode title (single file mode)')
    parser.add_argument('--description', help='Episode description (single file mode)')
    parser.add_argument('--season', type=int, default=1, help='Season number (single file mode)')
    parser.add_argument('--number', type=int, default=1, help='Episode number within the season (single file mode)')
    parser.add_argument('--explicit', action='store_true', help='Mark episode as explicit (single file mode)')
    parser.add_argument('--private', action='store_true', help='Mark episode as private (single file mode)')
    
    # Options for batch processing
    parser.add_argument('--batch-csv', help='Path to CSV file with batch upload data')
    parser.add_argument('--audio-files', nargs='+', help='List of audio files to upload (without metadata)')

    args = parser.parse_args()

    uploader = MaveDigitalUploader()

    try:
        # Step 1: Login (always required)
        uploader.login(args.email, args.password)

        if args.batch_csv:
            # Batch mode with CSV file
            episodes_data = process_episodes_from_csv(args.batch_csv)
            episode_ids = []
            
            # Upload all audio files first
            for episode in episodes_data:
                try:
                    episode_id = uploader.upload_audio(args.podcast_id, episode['audio_file'])
                    episode['episode_id'] = episode_id
                    episode_ids.append(episode_id)
                except Exception as e:
                    print(f"Skipping {episode['audio_file']} due to error: {str(e)}")
                    continue
            
            # Then publish all episodes
            uploader.publish_multiple_episodes(episodes_data)
            
        elif args.audio_files:
            # Batch mode with just audio files (no metadata)
            episode_ids = uploader.upload_multiple_audios(args.podcast_id, args.audio_files)
            print(f"Uploaded {len(episode_ids)}/{len(args.audio_files)} audio files successfully")
            
        elif args.audio_file:
            # Single file mode
            episode_id = uploader.upload_audio(args.podcast_id, args.audio_file)
            uploader.publish_episode(
                episode_id,
                args.title,
                args.description,
                is_explicit=args.explicit,
                is_private=args.private,
                season=args.season,
                number=args.number
            )
            print("Podcast episode uploaded and published successfully!")
        else:
            print("Error: You must specify either --audio-file or --batch-csv or --audio-files")
            return

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
