from pydub import AudioSegment

sound = AudioSegment.from_mp3("./ETHRAYUM_DHAYAYULLA_MATHAVE.MP3")
sound.export("./ETHRAYUM_DHAYAYULLA_MATHAVE.WAV", format="wav")
