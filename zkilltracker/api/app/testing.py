import requests
from jose import jwt

SSO_META_DATA_URL = "https://login.eveonline.com/.well-known/oauth-authorization-server"
JWK_ALGORITHM = "RS256"
JWK_ISSUERS = ("login.eveonline.com", "https://login.eveonline.com")
JWK_AUDIENCE = "EVE Online"


def validate_eve_jwt(token: str) -> dict:
    """Validate a JWT access token retrieved from the EVE SSO.

    Args:
        token: A JWT access token originating from the EVE SSO
    Returns:
        The contents of the validated JWT access token if there are no errors
    """
    # fetch JWKs URL from meta data endpoint
    res = requests.get(SSO_META_DATA_URL)
    res.raise_for_status()
    data = res.json()

    try:
        jwks_uri = data["jwks_uri"]
    except KeyError:
        raise RuntimeError(
            f"Invalid data received from the SSO meta data endpoint: {data}"
        )

    # fetch JWKs from endpoint
    res = requests.get(data["jwks_uri"])
    res.raise_for_status()
    data = res.json()

    try:
        jwk_sets = data["keys"]
    except KeyError:
        raise RuntimeError(f"Invalid data received from the the jwks endpoint: {data}")

    # pick the JWK with the requested alogorithm
    jwk_set = [item for item in jwk_sets if item["alg"] == JWK_ALGORITHM].pop()

    # try to decode the token and validate it against expected values
    # will raise JWT exceptions if decoding fails or expected values do not match
    contents = jwt.decode(
        token=token,
        key=jwk_set,
        algorithms=jwk_set["alg"],
        issuer=JWK_ISSUERS,
        audience=JWK_AUDIENCE,
    )
    return contents


if __name__ == "__main__":
    contents = validate_eve_jwt(
        "eyJhbGciOiJSUzI1NiIsImtpZCI6IkpXVC1TaWduYXR1cmUtS2V5IiwidHlwIjoiSldUIn0.eyJqdGkiOiIzYjc3OTM4Ny0xZWE4LTRjMDUtOTBlNC1kNDhmYTUxMTk1ODYiLCJraWQiOiJKV1QtU2lnbmF0dXJlLUtleSIsInN1YiI6IkNIQVJBQ1RFUjpFVkU6MjExOTkyNzI1MCIsImF6cCI6ImRjY2M4YWI0MWM1YzQwOTE5MTQxMmYxNTZjODU2NGViIiwidGVuYW50IjoidHJhbnF1aWxpdHkiLCJ0aWVyIjoibGl2ZSIsInJlZ2lvbiI6IndvcmxkIiwiYXVkIjpbImRjY2M4YWI0MWM1YzQwOTE5MTQxMmYxNTZjODU2NGViIiwiRVZFIE9ubGluZSJdLCJuYW1lIjoiTnVsbHVtIEluYW5pcyIsIm93bmVyIjoiSzJZNnkyaXhBMmQzRTJ0VmM3MlZNTVpqaG1NPSIsImV4cCI6MTczNTEyNjM2MSwiaWF0IjoxNzM1MTI1MTYxLCJpc3MiOiJodHRwczovL2xvZ2luLmV2ZW9ubGluZS5jb20ifQ.V_5P6W9YTLhZmYpjkhcc4SGtrVSeT7pt-TYLA-YikTbHqVlu-Mdd9X4xhUQpdQ0x65lP6zqoTcVnc4v1e1HTajQS_iOlN9LM25A7kr2m6ToMiduYszIf8ls37z3j7rcoLlgJ0M0Jy3paZ-kOvF3b5dhkpZ_Hv2kyO2x20_5NRDRE7DUenzYGzGvBl1iB4pEjWNO_CQvFHiOIKkyxTqMz1ae-9P3PAA4Iq50kdm2cIVEgXRgC0mscVpXDr_ygAqRC5NUiHKgz4m6viGMxuEHGERzb3E8F37XLelUB7A7VgefsvRbEsBAXEqiBXbAxWPu_8S2ZwTGdPqt-0AQw8TDXgw"
    )
    print("contents")
    print(contents)

    # import base64
    # import requests

    # # Replace these values with your client ID, client secret, and the authorization code you received
    # client_id = "dccc8ab41c5c409191412f156c8564eb"
    # client_secret = "wbyAzdG2bUB6FShmmhKXntfeejultYvbjhZJ5BGF"
    # authorization_code = "MMi6y9W8RkyVfCq6uOR06Q"

    # # Create the form-encoded values
    # payload = {"grant_type": "authorization_code", "code": authorization_code}

    # # Create the Base64 encoded credentials
    # credentials = f"{client_id}:{client_secret}"
    # encoded_credentials = base64.b64encode(credentials.encode()).decode()

    # # Set up the headers
    # headers = {
    #     "Authorization": f"Basic {encoded_credentials}",
    #     "Content-Type": "application/x-www-form-urlencoded",
    #     "Host": "login.eveonline.com",
    # }

    # # Send the POST request
    # url = "https://login.eveonline.com/v2/oauth/token"
    # response = requests.post(url, data=payload, headers=headers)

    # print(response)

    # # Check the response
    # if response.status_code == 200:
    #     print("Access Token:", response.json())
    # else:
    #     print("Error:", response.status_code, response.text)
