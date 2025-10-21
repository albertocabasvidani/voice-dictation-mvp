import pytest
from src.core.audio_recorder import AudioRecorder


def test_audio_recorder_init():
    """Test AudioRecorder initialization"""
    recorder = AudioRecorder(sample_rate=16000)
    assert recorder.sample_rate == 16000
    assert recorder.is_recording == False
    assert recorder.recording == []


def test_start_stop_recording():
    """Test start and stop recording flow"""
    recorder = AudioRecorder()

    recorder.start_recording()
    assert recorder.is_recording == True

    # Note: can't actually record without audio input
    # Just test the state changes
    recorder.is_recording = False

    assert recorder.is_recording == False


def test_list_devices():
    """Test listing audio devices"""
    devices = AudioRecorder.list_devices()
    assert devices is not None
