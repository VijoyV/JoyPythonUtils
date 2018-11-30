#!/usr/bin/env python3

"""
This python utility is to
    1. Register a user profile for future enrollment & verification.
    2. Enroll a user for voice based authentication (one time activity) using standard english "Phrase".
    3. Authenticate a user with the voice and the same 'Phrase' used for registration.
    4. get all registered user profiles
    5. get all allowed enrollment / verification phrases.

    @author: Vijoy Vallachira (vijoye@gmail.com)

    REF:
    https://azure.microsoft.com/en-in/services/cognitive-services/speaker-recognition/

    API DOCS (Speaker Reecognition API):
    https://westus.dev.cognitive.microsoft.com/docs/services?page=2

    API:
    https://westus.api.cognitive.microsoft.com/spid/v1.0

    API Level
    Python 3.2 or above
"""

import http.client, urllib.request, urllib.parse, urllib.error, base64, sys

httpHeaders = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '4918719bc5bf4fe8adb026c98aecd3f0',
}

'''
    1. To register a user profile,
'''
def createVerificationProfile():
    params = urllib.parse.urlencode({}
                                    )
    requestBody = '{ \'locale\' : \'en-us\' }'

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/spid/v1.0/verificationProfiles?%s" % params, requestBody, httpHeaders)

        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


'''
    2. Enroll a User Voice for Authentication [3 Successful Attempts are Required]
'''
def enrollVerificationProfile():
    params = urllib.parse.urlencode({
        # Request parameters
        'shortAudio': 'true',
    })

    requestBody = 'content of audio file in ascii format'

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/spid/v1.0/verificationProfiles/{verificationProfileId}/enroll?%s" % params, "{body}",
                     httpHeaders)
        response = conn.getresponse()
        data = response.read()
        print(format(data))
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

'''
    4. Get all registered users.
'''
def getAllEnrolledUsers():
    params = urllib.parse.urlencode({
    })



'''
    5. Get all MS AZure Speech Recognition Enrollment and verification phrases.
'''
def enrollmentVerificationPhrases():
    params = urllib.parse.urlencode({
    })

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/spid/v1.0/verificationPhrases?locale=en-us&%s" % params, "{body}", httpHeaders)
        response = conn.getresponse()
        data = response.read()
        print(format(data))
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def main():
    program_name = sys.argv[0]

    allowed_sub_commands = ["register", "enroll", "authenticate", "phrases", "users"]
    sub_command = sys.argv[1]

    if sub_command == "phrases" :
        enrollmentVerificationPhrases()
    else :
        print ("Other commands {0} not supported ", sub_command )


    # for x in sys.argv:
    #     print ("Argument: {} ", format(x))


if __name__ == '__main__' :
    main()
