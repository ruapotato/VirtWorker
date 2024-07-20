import os
import sys
import json
import time
import torch
from melo.api import TTS

# Add the necessary directories to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
openvoice_dir = os.path.join(current_dir, 'openvoice')
sys.path.insert(0, current_dir)
sys.path.insert(0, openvoice_dir)

from openvoice import se_extractor
from openvoice.api import ToneColorConverter

def run_voice_service():
    print("Starting voice service...")

    # Initialize ToneColorConverter
    ckpt_converter = os.path.join(current_dir, 'checkpoints_v2', 'checkpoints_v2', 'converter')
    config_path = os.path.join(ckpt_converter, 'config.json')
    checkpoint_path = os.path.join(ckpt_converter, 'checkpoint.pth')

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    tone_color_converter = ToneColorConverter(config_path, device=device)
    tone_color_converter.load_ckpt(checkpoint_path)

    # Initialize TTS
    tts_model = TTS(language='EN', device=device)

    # Get the 'en-au' speaker ID
    speaker_id = tts_model.hps.data.spk2id['en_au'] if 'en_au' in tts_model.hps.data.spk2id else 0

    request_dir = 'tts_requests'
    output_dir = 'tts_output'
    os.makedirs(request_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    while True:
        # Check for TTS requests
        for filename in os.listdir(request_dir):
            if filename.endswith('.json'):
                request_path = os.path.join(request_dir, filename)
                with open(request_path, 'r') as f:
                    request = json.load(f)
                
                text = request['text']
                output_filename = request['output_filename']
                
                print(f"Processing TTS request: {text[:50]}...")
                
                # Generate initial audio
                tmp_path = os.path.join(output_dir, 'tmp.wav')
                tts_model.tts_to_file(text, speaker_id, tmp_path)

                # Apply voice conversion
                output_path = os.path.join(output_dir, output_filename)
                reference_speaker = os.path.join(current_dir, 'resources', 'example_reference.wav')
                target_se, _ = se_extractor.get_se(reference_speaker, tone_color_converter, vad=False)
                source_se = torch.load(os.path.join(current_dir, 'checkpoints_v2', 'checkpoints_v2', 'base_speakers', 'ses', 'en-au.pth'), map_location=device)

                tone_color_converter.convert(
                    audio_src_path=tmp_path,
                    src_se=source_se,
                    tgt_se=target_se,
                    output_path=output_path
                )
                
                # Remove temporary file
                os.remove(tmp_path)
                
                print(f"TTS output saved to {output_path}")
                
                # Remove the processed request
                os.remove(request_path)
        
        time.sleep(1)  # Check for new requests every second

if __name__ == "__main__":
    run_voice_service()
