LATIN_1_CHARS = (
    (b'\xe2\x80\x99', b"'"),
    (b'\xc3\xa9', b'e'),
    (b'\xe2\x80\x90', b'-'),
    (b'\xe2\x80\x91', b'-'),
    (b'\xe2\x80\x92', b'-'),
    (b'\xe2\x80\x93', b'-'),
    (b'\xe2\x80\x94', b'-'),
    (b'\xe2\x80\x94', b'-'),
    (b'\xe2\x80\x98', b"'"),
    (b'\xe2\x80\x9b', b"'"),
    (b'\xe2\x80\x9c', b'"'),
    (b'\xe2\x80\x9c', b'"'),
    (b'\xe2\x80\x9d', b'"'),
    (b'\xe2\x80\x9e', b'"'),
    (b'\xe2\x80\x9f', b'"'),
    (b'\xe2\x80\xa6', b'...'),
    (b'\xe2\x80\xb2', b"'"),
    (b'\xe2\x80\xb3', b"'"),
    (b'\xe2\x80\xb4', b"'"),
    (b'\xe2\x80\xb5', b"'"),
    (b'\xe2\x80\xb6', b"'"),
    (b'\xe2\x80\xb7', b"'"),
    (b'\xe2\x81\xba', b"+"),
    (b'\xe2\x81\xbb', b"-"),
    (b'\xe2\x81\xbc', b"="),
    (b'\xe2\x81\xbd', b"("),
    (b'\xe2\x81\xbe', b")")
)


def clean_string(s: str):
    data = s.encode('utf-8').strip()
    for _hex, _char in LATIN_1_CHARS:
        data = data.replace(_hex, _char)

    from lxml.html.clean import clean_html
    from lxml.html import fromstring
    return fromstring(clean_html(data.decode('utf-8'))).text_content().strip()
