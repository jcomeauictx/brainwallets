#!/usr/bin/python3 -OO
'''
generate Bitcoin addresses from wordlists, and check the balance of each

use csv balances file created by btcposbal2csv
'''
from __future__ import print_function
import sys, os, hashlib, ecdsa, base58, re, logging
from binascii import unhexlify, hexlify  # reliable across most Python versions
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.WARN)

def generate_private_and_public_keys(secret, repeat):
    '''
    if `secret` is 64 hexadecimal digits, decode as binary string

    otherwise, generate sha256 hash and use that instead

    >>> generate_private_and_public_keys(
    ... '0C28FCA386C7A227600B2FE50B7CAE11'
    ... 'EC86D3BF1FBE471BE89827E19D72AA1D', 1)[0]
    '5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ'
    >>> generate_private_and_public_keys('satoshi nakamoto', 1)[0]
    '5K7EWwEuJu9wPi4q7HmWQ7xgv8GxZ2KqkFbjYMGvTCXmY22oCbr'
    '''
    try:
        if len(secret) != 64:
            raise TypeError('not a sha256 hash')
        secret = unhexlify(secret)
        # since we're not hashing the key, let's hash one less than repeat
        secret = sha256d(secret, reps=repeat - 1)
    except TypeError:
        logging.info('converting "%s" to sha256 hexdigest first', secret)
        secret = sha256d(secret.encode(), reps=repeat)
    signing_key = ecdsa.SigningKey.from_string(secret, curve=ecdsa.SECP256k1)
    verifying_key = signing_key.verifying_key
    public_key = b'04' + hexlify(verifying_key.to_string())
    private_key = b'\x80' + signing_key.to_string()
    wifkey = base58.b58encode(private_key + sha256d(private_key)[:4])
    return plainstring(wifkey), public_key

def plainstring(string):
    '''
    make sure string representation doesn't start with b or u

    just for making doctests pass regardless of python version. string
    must be ASCII.
    '''
    if repr(string).startswith("b'"):  # only python3 doess this
        return string.decode()
    elif repr(string).startswith("u'"):  # only python2 does this
        return string.encode()
    else:
        return string

def get_address(public_key):
    '''
    return public key in Wallet Import Format (WIF)
    '''
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(sha256d(unhexlify(public_key), 1))
    prefix = b'00' + hexlify(ripemd160.digest())
    checksum = sha256d(unhexlify(prefix), 2)[0:4]
    binary_addr = prefix + hexlify(checksum)
    return base58.b58encode(unhexlify(binary_addr))

def get_keys(secret, repeat=1):
    '''
    main routine
    '''
    logging.debug('Generating keys from passphrase %s, %d reps', secret, repeat)
    private_key, public_key = generate_private_and_public_keys(secret, repeat)
    #logging.debug('Private_key: %s', private_key)
    #logging.debug('Public key: %s', public_key)
    address = get_address(public_key)
    #logging.debug('Bitcoin address: %s', wif)
    return plainstring(address), private_key

def sha256d(data, reps=2):
    '''
    get sha256, sha256d, or any number of repeated hashes of any arbitrary data
    '''
    logging.debug('getting sha256 digest for %r, count=%d', data, reps)
    for count in range(reps):
        sha256 = hashlib.sha256(data)
        logging.debug('result %d: %s', count, sha256.hexdigest())
        data = sha256.digest()
    return data

def guess(repeatcount, addresslist, wordlists, suffixes):
    '''
    process keyphrases and check balance of resulting wallet addresses
    '''
    prefixes = set()
    suffixes.insert(0, '')
    with open(addresslist, 'r') as infile:
        for line in infile:
            if line.startswith('1'):
                prefixes.add(line[1:9])
    logging.debug('prefixes: %s', list(prefixes)[:10])
    for wordlist in wordlists:
        with open(wordlist, 'r') as infile:
            for word in infile:
                for suffix in set(suffixes):
                    keyword = (' '.join((word.rstrip(), suffix))).strip()
                    for repetitions in range(1, repeatcount + 1):
                        address, private_key = get_keys(keyword, repetitions)
                        if address[1:9] in prefixes:
                            logging.warning('Found %s in prefixes', address[:9])
                            check_match(addresslist, address, private_key,
                                        keyword, str(repetitions))

def check_match(addresslist, address, private_key, keyword, hashcount):
    '''
    check addresslist for match, print keys and balance if found
    '''
    with open(addresslist) as infile:
        for line in infile:
            try:
                btcaddress, satoshis, suffix = line.split(',')
            except ValueError:
                logging.error('Skipping malformed line %r', line.rstrip())
            if address == btcaddress:
                logging.warning('Found match for %s at %s', keyword, address)
                show([keyword, hashcount, address, private_key, satoshis])
                return
    logging.warning('No actual match found for %s at %s', keyword, address)

def show(result):
    '''
    print result as space-separated string.

    flush output so that tail -f on the output file shows results in real time
    '''
    string = ' '.join(result)
    try:
        print(string, flush=True)
    except TypeError:  # python2 doesn't support "flush"
        print(string)

if __name__ == '__main__':
    if not len(sys.argv) > 3:
        raise ValueError('Must specify repeat count, addresslist, wordlist[s]')
    COUNT = int(sys.argv[1])
    ADDRESSLIST = sys.argv[2]
    WORDLISTS, SUFFIXLIST = [], []
    for ARG in sys.argv[3:]:
        if os.path.isfile(ARG):
            WORDLISTS.append(ARG)
        else:
            SUFFIXLIST.append(ARG)
    guess(COUNT, ADDRESSLIST, WORDLISTS, SUFFIXLIST)
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
