import gzip
import base64

def decompress(compressed, base64_encoded = True):
    """ gzip으로 압축된 데이터를 푸는 메소드 """
    source = compressed
    if base64_encoded:
        source = base64.standard_b64decode(compressed)

    return gzip.decompress(source).decode('utf-8')
