import os

from google.cloud import texttospeech
from config import Config
from pygame import mixer
import tempfile

class AudioPlayer:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = Config.GOOGLE_CREDENTIALS
        self.client = texttospeech.TextToSpeechClient()
        self.playing = False
        self.paused = False
        self.current_audio = None
        self.voice = None
        self.paused_position = 0
        self._init_mixer()

    def _init_mixer(self):
        """Khởi tạo pygame mixer một cách an toàn"""
        if not mixer.get_init():
            try:
                mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
                print("Mixer initialized successfully")
            except Exception as e:
                print(f"Không thể khởi tạo mixer: {str(e)}")

    def text_to_speech(self, text, voice_name="vi-VN-Wavenet-A"):
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="vi-VN",
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return response.audio_content

    def play_audio(self, audio_content, start_pos=0):
        try:
            # Tạo file tạm để phát
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_content)
                temp_file = f.name
            print(f.name)
            self._init_mixer()

            mixer.music.load(temp_file)
            mixer.music.play(start=start_pos)

            self.playing = True
            self.paused = False
        except Exception as e:
            print(f"Lỗi phát audio: {e}")
            self.stop()

    def pause(self):
        if self.playing and not self.paused:
            mixer.music.pause()
            self.paused_position = mixer.music.get_pos() / 1000  # Lưu vị trí (giây)
            self.paused = True

    def resume(self):
        if self.paused:
            mixer.music.unpause()
            self.paused = False
        else:
            # Phát từ vị trí đã lưu nếu không ở trạng thái paused
            mixer.music.play(start=self.paused_position)
        self.playing = True

    def stop(self):
        if mixer.get_init():
            mixer.music.stop()
            self.playing = False
            self.paused = False

    def is_playing(self):
        return mixer.music.get_busy()

    def get_current_position(self, old_position):
        # Trả về vị trí hiện tại tính bằng giây
        return old_position + mixer.music.get_pos() / 1000
