# Mave.Digital Podcast Uploader

A Python script for uploading and publishing podcast episodes to platform. Supports both single and batch uploads.

## Features

- Single episode upload with metadata
- Batch upload of multiple audio files
- CSV-based batch processing with full metadata support
- Automatic waiting for audio processing to complete
- Error handling for individual files in batch mode

## Installation

1. Ensure you have Python 3.6 or later installed
2. Clone this repository or download the script
3. Install required dependencies (none beyond standard library)

## Usage

### Single Episode Mode

```bash
python native_execution.py \
    --email your@email.com \
    --password your_password \
    --podcast-id YOUR_PODCAST_ID \
    --audio-file episode.mp3 \
    --title "Episode Title" \
    --description "Episode description" \
    [--season 1] \
    [--number 1] \
    [--explicit] \
    [--private]
```

### Batch Audio Files Upload (without metadata)

```bash
python native_execution.py \
    --email your@email.com \
    --password your_password \
    --podcast-id YOUR_PODCAST_ID \
    --audio-files episode1.mp3 episode2.mp3 episode3.mp3
```

### CSV Batch Mode

1. Create a CSV file with episode data (see example below)
2. Run the script:

```bash
python native_execution.py \
    --email your@email.com \
    --password your_password \
    --podcast-id YOUR_PODCAST_ID \
    --batch-csv episodes.csv
```

### CSV File Format

Create a CSV file with the following columns (headers required):

```
audio_file,title,description,season,number,is_explicit,is_private
```

Example:

```csv
audio_file,title,description,season,number,is_explicit,is_private
ep1.mp3,Episode 1,First episode,1,1,false,false
ep2.mp3,Episode 2,Second episode,1,2,true,false
ep3.mp3,Episode 3,Third episode,1,3,false,true
```

## Error Handling

- In batch modes, the script will continue processing remaining files if an error occurs with one file
- Errors are logged to console with details
- Successfully uploaded files are reported

## Limitations

- Currently only supports MP3 audio files (can be modified in code if needed)
- Requires stable internet connection during upload
- Large batches may take significant time to process

## License

This script is provided as-is without warranty. Use at your own risk.

---

For support or feature requests, please open an issue in the repository.
