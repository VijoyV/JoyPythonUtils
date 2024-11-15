from pydub import AudioSegment

sound = AudioSegment.from_mp3("songs/NITHYA_SOUJANYA_DHAYAKA_KARTHAVE_SREE_YESU_NAATHA.MP3")
sound.export("./NITHYA_SOUJANYA_DHAYAKA_KARTHAVE_SREE_YESU_NAATHA.WAV", format="wav")
