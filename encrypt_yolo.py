from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import argparse
import sys

def rc4_crypt(key, input_file, output_file):
    # Initialize the RC4 state
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]

    # Read the input file
    with open(input_file, 'rb') as file:
        data = bytearray(file.read())

    # Encrypt or decrypt the data using the RC4 state
    i = 0
    j = 0
    for k in range(len(data)):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        data[k] ^= S[(S[i] + S[j]) % 256]

    # Write the encrypted or decrypted content to the output file
    with open(output_file, 'wb') as file:
        file.write(data)

# Encrypt/Decrypt some file with RC4 scheme 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_file', type=str,
                        help='directory to weight file to be encrypted', default='yolov4.cfg')
    parser.add_argument('--key_file', type=str,
                        help='directory to key file', default = 'key.bin')
    
    args = parser.parse_args(sys.argv[1:])

    with open(args.key_file, 'rb') as key_file:
        key = key_file.read()

    # Encrypt / Decrypt
    rc4_crypt(key, args.input_file, args.input_file+".crypt")