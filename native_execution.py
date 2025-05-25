#!/usr/bin/env python3
import json
import os
import argparse
import urllib.request
import urllib.parse
import urllib.error
import random
import string

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

    def login(self, email, password):
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

        # Create request
        request = urllib.request.Request(url, method='POST')
        for key, value in headers.items():
            request.add_header(key, value)

        # Add data to request
        request.data = json.dumps(data).encode('utf-8')

        try:
            # Send request
            response = self.opener.open(request)
            response_data = json.loads(response.read().decode('utf-8'))

            # Store tokens
            self.access_token = response_data.get('access_token')
            self.refresh_token = response_data.get('refresh_token')
            self.user_id = response_data.get('user', {}).get('id')

            print(f"Login successful for user: {response_data.get('user', {}).get('name')}")
            return response_data

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            raise Exception(f"Login failed: {e.code} - {error_message}")

    def upload_audio(self, podcast_id, audio_file_path):
        """Upload audio file to mave.digital"""
        if not self.access_token:
            raise Exception("Not logged in. Call login() first.")

        url = f"{self.base_url}/episodes/upload-audio"

        # Generate boundary for multipart form
        boundary = '----WebKitFormBoundary' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

        # Prepare multipart form data
        with open(audio_file_path, 'rb') as f:
            file_data = f.read()

        # Create form data with proper line breaks
        body = []
        # Add file part
        body.append(f'--{boundary}'.encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="audio"; filename="{os.path.basename(audio_file_path)}"'.encode('utf-8'))
        body.append(b'Content-Type: audio/mpeg')
        body.append(b'')
        body.append(file_data)

        # Add podcast_id part
        body.append(f'--{boundary}'.encode('utf-8'))
        body.append(f'Content-Disposition: form-data; name="podcast_id"'.encode('utf-8'))
        body.append(b'')
        body.append(podcast_id.encode('utf-8'))

        # Add closing boundary
        body.append(f'--{boundary}--'.encode('utf-8'))

        # Join all parts with CRLF
        multipart_data = b'\r\n'.join(body)

        # Create request
        request = urllib.request.Request(url, method='POST')
        request.add_header('Authorization', f'Bearer {self.access_token}')
        request.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        request.data = multipart_data

        try:
            # Send request
            response = self.opener.open(request)
            response_data = json.loads(response.read().decode('utf-8'))

            episode_id = response_data.get('episode_id')
            print(f"Audio uploaded successfully. Episode ID: {episode_id}")

            # Wait for audio processing to complete
            self._wait_for_audio_processing(episode_id)

            return episode_id

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            raise Exception(f"Upload failed: {e.code} - {error_message}")

    def _wait_for_audio_processing(self, episode_id):
        """Wait for audio processing to complete by polling the audio-status endpoint"""
        url = f"{self.base_url}/episodes/{episode_id}/audio-status"

        print("Waiting for audio processing to complete...")

        max_attempts = 30  # Maximum number of polling attempts
        delay_seconds = 2  # Initial delay between polling attempts

        for attempt in range(max_attempts):
            try:
                # Create request
                request = urllib.request.Request(url, method='GET')
                request.add_header('Authorization', f'Bearer {self.access_token}')
                request.add_header('Accept', 'application/json')

                # Send request
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

            # Exponential backoff with a maximum delay of 10 seconds
            import time
            time.sleep(min(delay_seconds * (1.5 ** attempt), 10))

        raise Exception(f"Audio processing timed out after {max_attempts} attempts")

    def publish_episode(self, episode_id, title, description, is_explicit=False, is_private=False, season=1, number=1, date=None):
        """Publish an episode on mave.digital"""
        if not self.access_token:
            raise Exception("Not logged in. Call login() first.")

        url = f"{self.base_url}/episodes/{episode_id}/publish"
        date = date if date is not None else __import__('datetime').datetime.now().strftime('%Y-%m-%d')

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
            'publish_date': date,
            'plans': []
        }

        # Create request
        request = urllib.request.Request(url, method='POST')
        for key, value in headers.items():
            request.add_header(key, value)

        # Add data to request
        request.data = json.dumps(data).encode('utf-8')

        try:
            # Send request
            response = self.opener.open(request)
            print(f"Episode '{title}' published successfully!")
            return True

        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            raise Exception(f"Publishing failed: {e.code} - {error_message}")


def main():
    parser = argparse.ArgumentParser(description='Upload podcasts to mave.digital')
    parser.add_argument('--email', required=True, help='Your mave.digital email')
    parser.add_argument('--password', required=True, help='Your mave.digital password')
    parser.add_argument('--podcast-id', required=True, help='ID of the podcast to upload to')
    parser.add_argument('--audio-file', required=True, help='Path to the audio file to upload')
    parser.add_argument('--title', required=True, help='Episode title')
    parser.add_argument('--description', required=True, help='Episode description')
    parser.add_argument('--season', type=int, default=1, help='Season number')
    parser.add_argument('--number', type=int, default=1, help='Episode number within the season')
    parser.add_argument('--date', default=1, help='Episode publish date')
    parser.add_argument('--explicit', action='store_true', help='Mark episode as explicit')
    parser.add_argument('--private', action='store_true', help='Mark episode as private')

    args = parser.parse_args()

    uploader = MaveDigitalUploader()

    try:
        # Step 1: Login
        uploader.login(args.email, args.password)

        # Step 2: Upload audio
        episode_id = uploader.upload_audio(args.podcast_id, args.audio_file)

        # Step 3: Publish episode
        uploader.publish_episode(
            episode_id,
            args.title,
            args.description,
            is_explicit=args.explicit,
            is_private=args.private,
            season=args.season,
            number=args.number,
            date=args.date
        )

        print("Podcast episode uploaded and published successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
