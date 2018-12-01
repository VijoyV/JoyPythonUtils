#!/usr/bin/env python3

"""
This python utility is to
    1. Register a user profile for future enrollment & verification with Microsoft Cognitive APIs (Speech)
    2. Enroll a registered user's voice for a voice based authentication (one time activity) using standard English phrases
    3. Authenticate a user with the voice and the same 'Phrase' used for enrollment (step #2).
    4. get all registered user profiles
    5. get all allowed enrollment / verification phrases from Microsoft Cognitive API Site.

    @author: Vijoy Vallachira (vijoye@gmail.com)

    REF:
    https://azure.microsoft.com/en-in/services/cognitive-services/speaker-recognition/

    API DOCS (Speaker Recognition API):
    https://westus.dev.cognitive.microsoft.com/docs/services?page=2

    API:
    https://westus.api.cognitive.microsoft.com/spid/v1.0

    Level
    Python 3.2 or above
"""

import http.client, urllib.request, urllib.parse, urllib.error, base64
import sys, json
import speech_recognition as sr


httpHeaders = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '4918719bc5bf4fe8adb026c98aecd3f0',
}

httpHeaders4MediaUpload = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '4918719bc5bf4fe8adb026c98aecd3f0',
}


'''
    1. To register a user profile,
'''
def registerVerificationProfile():

    print("\n==> In registerVerificationProfile(): \n")

    userName  = input("Enter User Name : ")

    print("Please wait .... We are registering you with Microsoft Speech Recognition API \n")

    params = urllib.parse.urlencode({}
                                    )
    requestBody = '{ \'locale\' : \'en-us\' }'

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/spid/v1.0/verificationProfiles?%s" % params, requestBody, httpHeaders)

        response = conn.getresponse()
        data = response.read().decode('utf-8')
        print(format(data))
        conn.close()

        print("Registration Success....! \nPlease make note of GUID for further steps. \n")


    except Exception as e:
        print("Registration Faile....!  [Errno {0}] {1}".format(e.errno, e.strerror))



'''
    2. Enroll a User Voice for Authentication [3 Successful Attempts are Required]
'''
def enrollVerificationProfile(profileId, preRecordedAudioFile):

    print("\n==> In enrollVerificationProfile(): \n")

    audioInputFile =''

    if (profileId) :
        print("Using Profile ID = ", profileId)
        if (preRecordedAudioFile) :
            print("Using Pre-Recorded Audio File  = ", preRecordedAudioFile)
            audioInputFile = preRecordedAudioFile
        else :
            '''
            A. Let us get the audio recorded and it's local WAV file name
            '''
            audioInputFile = recordPhrase(profileId)
    else :
        print("\nNo Profile Id mentiond..... CAN NOT Proceed Further....!! ")
        exit(1)

    params = urllib.parse.urlencode({
        # Request parameters
        'shortAudio': 'true',
    })


    print("\nVoice File created locally as " + audioInputFile
          + "\nPlease wait .... We are registering your voice with Microsoft Cognitive API Server \n")

    try:
        '''
         B.  Let us read the audio WAV file in binary form to construct the body.
        '''
        # Prepare the body of the message
        with open(audioInputFile, mode='rb') as file:  # b is important -> binary
            body = file.read()

        '''
         C.  Let us submit teh file to API and wait for result.
        '''

        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')

        # Prepare the request
        _VERIFICATION_URI = '/spid/v1.0/verificationProfiles/{0}/enroll?%s'.format(urllib.parse.quote(profileId))

        print("Verification URI =" + _VERIFICATION_URI)

        conn.request("POST", _VERIFICATION_URI % params, body,
                     httpHeaders4MediaUpload)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        print(format(data))
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


'''
    3. Authenticate Enrolled User Profile. 
'''
def authenticateVerificationProfile(profileId, preRecordedAudioFile):

    print("\n==> In authenticateVerificationProfile(): \n")

    audioInputFile =''

    if (profileId) :
        print("Using Profile ID = ", profileId)
        if (preRecordedAudioFile) :
            print("Using Pre-Recorded Audio File  = ", preRecordedAudioFile)
            audioInputFile = preRecordedAudioFile
        else :
            '''
            A. Let us get the audio recorded and it's local WAV file name
            '''
            audioInputFile = recordPhrase(profileId)
    else :
        print("\nNo Profile Id mentiond..... CAN NOT Proceed Further....!! ")
        exit(1)

    params = urllib.parse.urlencode({
        # Request parameters
        'shortAudio': 'true',
    })


    print("\nVoice File created locally as " + audioInputFile
          + "\nPlease wait .... We are Verifying (Authenticate) your voice with Microsoft Cognitive API Server \n")

    try:
        '''
         B.  Let us read the audio WAV file in binary form to construct the body.
        '''
        # Prepare the body of the message
        with open(audioInputFile, mode='rb') as file:  # b is important -> binary
            body = file.read()

        '''
         C.  Let us submit the file to API and wait for result.
        '''

        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')

        # Prepare the request
        _VERIFICATION_URI = '/spid/v1.0/verify?verificationProfileId={0}&%s'.format(urllib.parse.quote(profileId))

        print("\nVerification URI =" + _VERIFICATION_URI)

        conn.request("POST", _VERIFICATION_URI % params, body,
                     httpHeaders4MediaUpload)

        response = conn.getresponse()
        data = response.read().decode('utf-8')
        print(format(data))
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

'''
    4. Get all registered users.
'''
def getAllEnrolledUsers():

    print("\n==> In getAllEnrolledUsers():")

    params = urllib.parse.urlencode({
    })

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/spid/v1.0/verificationProfiles?%s" % params, "{body}", httpHeaders)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        print(format(data))
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


'''
    5. Get all MS AZure Speech Recognition Enrollment and verification phrases.
'''
def enrollmentVerificationPhrases():

    print("\n==> In enrollmentVerificationPhrases():")

    params = urllib.parse.urlencode({
    })

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/spid/v1.0/verificationPhrases?locale=en-us&%s" % params, "{body}", httpHeaders)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        print(format(data))
        # json.load(data)
        # print(json.dump())
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

"""
private / utility functions 
"""

def recordPhrase(profileId) :

    # obtain audio from the microphone

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n\nPlease speak the following phrase: ")
        print("\n\n\'My Password is not your business'\n")
        audio = r.listen(source)

    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("\nGoogle thinks you said '" + r.recognize_google(audio) + "'\n")

        # write audio to a WAV file
        audioFileName = "./voice-files/"+profileId+".wav"
        with open(audioFileName, "wb") as f:
            f.write(audio.get_wav_data())

        return audioFileName

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def main():
    program_name = sys.argv[0]

    allowed_sub_commands = ["register", "enroll", "authenticate", "phrases", "users"]
    sub_command = sys.argv[1]

    if sub_command == "register":
        registerVerificationProfile()
    elif sub_command == "enroll" :
        enrollVerificationProfile(sys.argv[2], sys.argv[3])
    elif sub_command == "authenticate":
        authenticateVerificationProfile(sys.argv[2], sys.argv[3])
    elif sub_command == "phrases" :
        enrollmentVerificationPhrases()
    elif sub_command == "users" :
        getAllEnrolledUsers()
    else :
        print ("This sub-command '{0}' not supported " .format(sub_command) )


    # for x in sys.argv:
    #     print ("Argument: {} ", format(x))


if __name__ == '__main__' :
    main()
