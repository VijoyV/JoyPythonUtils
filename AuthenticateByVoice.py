'''
This python utility is
    1. To register a user profile,
    2. Enroll him/her for a voice based authentication (one time activity) using standard english phrases, and finally
    3. To authenticate him using his voice and same 'Phrase' used for registration.

    @author / @assembler : Vijoy Vallachira (vijoye@gmail.com)

    REF:
    https://azure.microsoft.com/en-in/services/cognitive-services/speaker-recognition/

    API DOCS (Speaker Reecognition API):
    https://westus.dev.cognitive.microsoft.com/docs/services?page=2

    API:
    https://westus.api.cognitive.microsoft.com/spid/v1.0

'''


import http.client, urllib.request, urllib.parse, urllib.error, base64

httpHeaders = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '4918719bc5bf4fe8adb026c98aecd3f0',
}


httpRequestparams = urllib.parse.urlencode( {}
)


'''
    1. To register a user profile,
'''
def createProfile() :

    requestBody = '{ \'locale\' : \'en-us\' }'

    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/spid/v1.0/identificationProfiles?%s" % httpRequestparams, requestBody, httpHeaders)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

