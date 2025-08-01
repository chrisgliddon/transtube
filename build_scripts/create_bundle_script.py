#!/usr/bin/env python3
"""
Create a bundled Python script for TransTube backend
"""
import os
import shutil

def create_script():
    """Create the main bundling script for the Python backend"""
    
    script_content = '''#!/usr/bin/env python3
"""
TransTube Backend - Bundled Entry Point
This script serves as the entry point for the bundled Python backend.
"""
import sys
import os
import json
import argparse
from pathlib import Path

# Add the bundled packages to Python path
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundle_dir = sys._MEIPASS
else:
    # Running in normal Python environment
    bundle_dir = Path(__file__).parent

# Import the main transcription module
sys.path.insert(0, str(bundle_dir))

# Import after path setup
from bulk_transcribe_youtube_videos_from_playlist import (
    process_single_video_async,
    download_semaphore,
    transcribe_audio_file,
    get_cuda_toolkit_path,
    add_to_system_path
)

def main():
    parser = argparse.ArgumentParser(description='TransTube Backend')
    parser.add_argument('--url', required=True, help='YouTube URL to process')
    parser.add_argument('--output-dir', default='transcripts', help='Output directory')
    parser.add_argument('--progress-callback', help='IPC endpoint for progress updates')
    parser.add_argument('--use-cuda', action='store_true', help='Enable CUDA if available')
    
    args = parser.parse_args()
    
    # Set up CUDA if requested
    if args.use_cuda:
        cuda_path = get_cuda_toolkit_path()
        if cuda_path:
            add_to_system_path(cuda_path)
    
    # Process the video
    try:
        import asyncio
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Run the async processing
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            process_single_video_async(args.url, args.output_dir)
        )
        
        # Return success
        print(json.dumps({
            'status': 'success',
            'transcript_path': result.get('transcript_path'),
            'metadata_path': result.get('metadata_path')
        }))
        
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'error': str(e)
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
'''
    
    # Write the bundling script
    bundle_script_path = 'build_scripts/transtube_backend.py'
    with open(bundle_script_path, 'w') as f:
        f.write(script_content)
    
    print(f"Created bundling script at: {bundle_script_path}")
    
    # Copy the main transcription script to build_scripts for bundling
    shutil.copy('bulk_transcribe_youtube_videos_from_playlist.py', 'build_scripts/')
    
    return bundle_script_path

if __name__ == '__main__':
    create_script()