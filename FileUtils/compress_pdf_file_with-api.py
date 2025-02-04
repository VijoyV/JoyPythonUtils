import requests


def get_jwt_token(public_key_str):

    post_url = "https://api.ilovepdf.com/v1/auth"
    data = {"public_key": public_key_str}
    response = requests.post(post_url, data=data)
    if response.status_code == 200:
        print(response.json()["token"])
        return response.json()["token"]
    else:
        raise Exception(f"Error obtaining JWT token: {response.status_code} - {response.text}")


def compress_pdf_with_ilovepdf(input_path, output_path, token):
    """
    Compresses a PDF file using iLovePDF API.

    :param input_path: Path to the input PDF file.
    :param output_path: Path to save the compressed PDF file.
    :param api_key: Your iLovePDF API key.
    """
    try:
        url = "https://www.ilovepdf.com/v1/compress-pdf"
        files = {"file": open(input_path, "rb")}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Compressed PDF saved at {output_path}")
        else:
            print(f"Error compressing PDF: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error compressing PDF: {e}")


# Example usage
input_file = "./Joanna_Aadhaar.pdf"  # Replace with your input directory
output_file = "./Joanna_Aadhaar_200KB.pdf"  # Replace with your output directory
public_key = "project_public_00837fb0d378430ced9b6f96e348fc90_4bKga565cb0efb713003c6eb2503178fd69e1"

token = get_jwt_token(public_key)

## This code does not work as it require to call a 4 -step work flow (API calls) to compress a PDF


# compress_pdf_with_ilovepdf(input_file, output_file, token)
