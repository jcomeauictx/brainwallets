#!/usr/bin/python3
'''
Minimal base58 encoder/decoder

Tried to use https://tools.ietf.org/id/draft-msporny-base58-01.html, but
coding the encoder to the spec gave wrong results, and the decoder instructions
make no sense.

So I ended up using //github.com/jgarzik/python-bitcoinlib/blob/master/
as a basis.

Copyright (C) 2021 jc@unternet.net
'''
import sys, os, logging

logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARN)

BASE58 = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

TEST_VECTORS = [
    # Note that the errors in the draft spec have been corrected below.
    [b'Hello World!', b'2NEpo7TZRRrLZSi2U'],
    [b'Hello, World!', b'72k1xXWG59fYdzSNoA'],
    [b'The quick brown fox jumps over the lazy dog.',
     b'USm3fpXnKG5EUBx2ndxBDMPVciP5hGey2Jh4NDv6gmeo1LkMeiKrLJUUBk6Z'],
    [b'\x00\x00\x00\x28\x7f\xb4\xcd', b'111233QC4'],
    [b'\x00\x00\x28\x7f\xb4\xcd', b'11233QC4'],
]

def encode(bytestring):
    '''
    Base58 encode bytstring

    >>> [encode(a) == b for a, b in TEST_VECTORS]
    [True, True, True, True, True]
    '''
    cleaned = bytestring.lstrip(b'\0')
    padding = BASE58[0:1] * (len(bytestring) - len(cleaned))
    number, unencoded, encoded = 0, bytearray(bytestring), bytearray()
    while unencoded:
        number = (number << 8) + unencoded.pop(0)
    while number:
        number, remainder = divmod(number, 58)
        encoded.append(BASE58[remainder])
    return (bytes(encoded) + padding)[::-1]

def decode(bytestring):
    '''
    Base58 decode bytestring

    >>> [decode(b) == a for a, b in TEST_VECTORS]
    [True, True, True, True, True]
    '''
    cleaned = bytestring.lstrip(BASE58[0:1])
    number, decoded = 0, bytearray()
    for byte in cleaned:
        number = (number * 58) + BASE58.index(byte)
    while number:
        decoded.append(number % 256)
        number >>= 8
    decoded += b'\0' * (len(bytestring) - len(cleaned))
    return bytes(decoded)[::-1]

if __name__ == '__main__':
    for decoded, encoded in TEST_VECTORS:
        logging.debug('checking encoding of %r', decoded)
        check = encode(decoded)
        if check != encoded:
            logging.error('%r does not match %r', check, encoded)
    for decoded, encoded in TEST_VECTORS:
        logging.debug('checking decoding of %r', encoded)
        check = decode(encoded)
        if check != decoded:
            logging.error('%r does not match %r', check, decoded)
else:
    # imported by other programs which expect pip-installed base58
    (b58encode, b58decode) = (encode, decode)
