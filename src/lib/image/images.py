from binascii import b2a_base64
from email import encoders


def format_image_html(msg, src_only: bool = False) -> str:
    # Image size reduction algorithm based on Mumble's c++ image encoding:
    # https://github.com/mumble-voip/mumble/blob/e0ad21139f1f822688b63b0da40a06df54c99fdc/src/mumble/Log.cpp#L572-L594
    encoders.encode_base64(msg)
    return msg


def encode_b64_test(byte_arr) -> str:
    # Encodes string byte array data to encoded base64 RFC-2045.
    encvec = []
    eol = "\n"
    max_unencoded = 76 * 3 // 4
    s = byte_arr
    for i in range(0, len(s), max_unencoded):
        enc = b2a_base64(s[i : i + max_unencoded]).decode("ascii")
        if enc.endswith("\n") and eol != "\n":
            enc = enc[:-1] + eol
        encvec.append(enc)

    b64_img = "".join(encvec)
    return b64_img
