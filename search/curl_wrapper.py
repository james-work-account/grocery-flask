import pycurl
import json
import io


def make_request(url: str, headers, is_json: bool, body=None):
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url.replace(' ', '%20'))
    curl.setopt(pycurl.HTTPHEADER, headers)
    # curl.setopt(pycurl.FOLLOWLOCATION, 1)

    if body is not None:
        curl.setopt(pycurl.POST, 1)
        body_as_json_string = json.dumps(body)  # dict to json
        body_as_file_object = io.StringIO(body_as_json_string)
        curl.setopt(pycurl.READDATA, body_as_file_object)
        curl.setopt(pycurl.POSTFIELDSIZE, len(body_as_json_string))

    # curl.setopt(pycurl.TIMEOUT_MS, 3000)

    response = io.BytesIO()
    curl.setopt(pycurl.WRITEFUNCTION, response.write)

    curl.perform()

    status_code = curl.getinfo(pycurl.RESPONSE_CODE)
    if status_code != 200:
        raise Exception(f"Aww Snap :( Server returned HTTP status code {status_code} and error {response.getvalue().decode('iso-8859-1')}")

    curl.close()

    if is_json:
        return json.loads(response.getvalue().decode('utf-8'))

    return response.getvalue().decode('utf-8')
