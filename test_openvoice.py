import os
import sys

# Add the voice_service directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
voice_service_dir = os.path.join(current_dir, 'voice_service')
openvoice_dir = os.path.join(voice_service_dir, 'openvoice')
sys.path.insert(0, voice_service_dir)
sys.path.insert(0, openvoice_dir)

import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS

def test_openvoice():
    print("Starting OpenVoice test...")

    # Print CUDA information
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"cuDNN version: {torch.backends.cudnn.version()}")
    print(f"Number of CUDA devices: {torch.cuda.device_count()}")
    
    if torch.cuda.is_available():
        print(f"Current CUDA device: {torch.cuda.current_device()}")
        print(f"CUDA device name: {torch.cuda.get_device_name(0)}")

    # Print LD_LIBRARY_PATH
    print(f"LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', 'Not set')}")

    # Initialization
    ckpt_converter = os.path.join(voice_service_dir, 'checkpoints_v2', 'checkpoints_v2', 'converter')
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    output_dir = 'outputs_v2'

    print(f"Using device: {device}")
    print(f"Checkpoint converter path: {ckpt_converter}")

    config_path = os.path.join(ckpt_converter, 'config.json')
    checkpoint_path = os.path.join(ckpt_converter, 'checkpoint.pth')

    print(f"Config path: {config_path}")
    print(f"Checkpoint path: {checkpoint_path}")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    tone_color_converter = ToneColorConverter(config_path, device=device)
    tone_color_converter.load_ckpt(checkpoint_path)

    os.makedirs(output_dir, exist_ok=True)

    # Obtain Tone Color Embedding
    reference_speaker = os.path.join(voice_service_dir, 'resources', 'example_reference.mp3')
    target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, vad=False)

    print(f"Extracted tone color embedding from: {reference_speaker}")

    # Use MeloTTS as Base Speakers
    texts = {
        'EN_NEWEST': "Did you ever hear a folk tale about a giant turtle?",
        'EN': "Did you ever hear a folk tale about a giant turtle?",
        'ES': "El resplandor del sol acaricia las olas, pintando el cielo con una paleta deslumbrante.",
    }

    src_path = os.path.join(output_dir, 'tmp.wav')
    speed = 1.0

    for language, text in texts.items():
        print(f"Processing language: {language}")
        model = TTS(language=language, device=device)
        speaker_ids = model.hps.data.spk2id
        
        for speaker_key in speaker_ids.keys():
            speaker_id = speaker_ids[speaker_key]
            speaker_key = speaker_key.lower().replace('_', '-')
            
            source_se = torch.load(os.path.join(voice_service_dir, 'checkpoints_v2', 'checkpoints_v2', 'base_speakers', 'ses', f'{speaker_key}.pth'), map_location=device)
            model.tts_to_file(text, speaker_id, src_path, speed=speed)
            save_path = os.path.join(output_dir, f'output_v2_{speaker_key}.wav')

            # Run the tone color converter
            encode_message = "@MyShell"
            tone_color_converter.convert(
                audio_src_path=src_path, 
                src_se=source_se, 
                tgt_se=target_se, 
                output_path=save_path,
                message=encode_message)
            
            print(f"Generated audio for {language} with speaker {speaker_key}: {save_path}")

    print("OpenVoice test completed successfully!")

if __name__ == "__main__":
    test_openvoice()
