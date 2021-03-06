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
from binascii import hexlify, unhexlify  # works on most versions of Python

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

def encode(bytestring=None, from_hex=False):
    '''
    Base58 encode bytstring

    >>> [encode(a) == b for a, b in TEST_VECTORS]
    [True, True, True, True, True]
    >>> encode('0123456789abcdef', True).decode() == 'C3CPq7c8PY'
    True
    '''
    if bytestring is None:
        logging.debug('no arg, attempting to read bytes from stdin')
        bytestring = getattr(sys.stdin, 'buffer', sys.stdin).read()
    elif not isinstance(bytestring, bytes):
        bytestring = bytes(bytestring.encode())
    if from_hex:
        bytestring = unhexlify(bytestring)
    logging.debug('base58 encoding %r...', bytestring[:64])
    cleaned = bytestring.lstrip(b'\0')
    padding = BASE58[0:1] * (len(bytestring) - len(cleaned))
    number, unencoded, encoded = 0, bytearray(bytestring), bytearray()
    while unencoded:
        number = (number << 8) + unencoded.pop(0)
    while number:
        number, remainder = divmod(number, 58)
        encoded.append(BASE58[remainder])
    return (bytes(encoded) + padding)[::-1]

def decode(bytestring=None, to_hex=False):
    '''
    Base58 decode bytestring

    >>> [decode(b) == a for a, b in TEST_VECTORS]
    [True, True, True, True, True]
    >>> decode('C3CPq7c8PY', True) == b'0123456789abcdef'
    True
    '''
    if bytestring is None:
        logging.debug('no arg, attempting to read bytes from stdin')
        bytestring = getattr(sys.stdin, 'buffer', sys.stdin).read()
    elif not isinstance(bytestring, bytes):
        bytestring = bytes(bytestring.encode())
    logging.debug('base58 decoding %r...', bytestring[:64])
    cleaned = bytestring.lstrip(BASE58[0:1])
    number, decoded = 0, bytearray()
    for byte in cleaned:
        try:
            number = (number * 58) + BASE58.index(byte)
        except TypeError:  # python3.1 bytearray doesn't implement buffer
            number = (number * 58) + list(BASE58).index(byte)
    while number:
        decoded.append(number % 256)
        number >>= 8
    decoded += b'\0' * (len(bytestring) - len(cleaned))
    decoded = bytes(decoded)[::-1]
    if to_hex:
        decoded = hexlify(decoded)
    return decoded

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Must specify action: "encode" or "decode"\r\n')
        sys.exit(1)
    elif sys.argv[1] not in ('encode', 'decode'):
        sys.stderr.write('Unknown action %s\r\n' % sys.argv[1])
        sys.exit(2)
    getattr(sys.stdout, 'buffer', sys.stdout).write(
        eval(sys.argv[1])(' '.join(sys.argv[2:]) if sys.argv[2:] else None))
else:
    # imported by other programs which expect pip-installed base58
    (b58encode, b58decode) = (encode, decode)
