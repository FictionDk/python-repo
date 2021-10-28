import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
from Crypto.Cipher import AES
from Crypto.Util.Padding import ( pad, unpad)
from base64 import (b64encode, b64decode)

class ZanthAES(object):

    def __init__(self, key='Zanthoxylum', mode='GCM'):
        self.__key = key
        # ass: associated_data, be authenticated but not encrypted
        self.__ass = b'authenticated but not encrypted payload'
        self.__mode = mode

    def _add_to_16(self, content):
        '''对密钥/偏移量进行长度填充
        Args:
            content 带填充值
        Returns: 返回符合规定长度的值(16,24,32 bytes)
        '''
        content = bytes(content, encoding='utf8')
        while len(content) % 16 != 0:
            content += b'\0'
        return content

    def _ecb_encrypt(self, text, key):
        '''对内容加密(ECB)
        Args:
            text 需要加密的原文
            key 处理密钥
        Returns: 返回加密后的内容
        '''
        key = self._add_to_16(key)
        text = text.encode('utf-8')
        cipher = AES.new(key, AES.MODE_ECB)
        data = cipher.encrypt(pad(text, AES.block_size))
        return b64encode(data).decode('utf-8')

    def _ecb_decrypt(self, text, key):
        try:
            key = self._add_to_16(key)
            text = b64decode(text.encode('utf-8'))
            cipher = AES.new(key, AES.MODE_ECB)
            pt = unpad(cipher.decrypt(text), AES.block_size)
            return pt.decode()
        except(ValueError, KeyError, Exception) as e:
            print("Incorrect decryption for text: %s from  key: %s; Error= %s" % (text,key,str(e)))
            return

    def _gcm_encrypt(self, key, plaintext, associated_data):
        key = self._add_to_16(key)

        # Generate a random 96-bit IV.
        iv = os.urandom(12)

        # Construct an AES-GCM Cipher object with the given key and a
        # randomly generated IV.
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()

        # associated_data will be authenticated but not encrypted,
        # it must also be passed in on decryption.
        encryptor.authenticate_additional_data(associated_data)

        # Encrypt the plaintext and get the associated ciphertext.
        # GCM does not require padding.
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return (iv, ciphertext, encryptor.tag)

    def _gcm_decrypt(self, key, associated_data, iv, ciphertext, tag):
        key = self._add_to_16(key)

        # Construct a Cipher object, with the key, iv, and additionally the
        # GCM tag used for authenticating the message.
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()

        # We put associated_data back in or the tag will fail to verify
        # when we finalize the decryptor.
        decryptor.authenticate_additional_data(associated_data)

        # Decryption gets us the authenticated plaintext.
        # If the tag does not match an InvalidTag exception will be raised.
        return decryptor.update(ciphertext) + decryptor.finalize()

    def set_key(self, key):
        self.__key = key

    def encrypt(self, text):
        '''对内容加密(默认)
        Args:
            text 字符串 需要加密的内容
        Returns: 字符串 返回加密后的内容,解密失败返回None
        '''
        key = self.__key
        if self.__mode == 'ECB':
            return self._ecb_encrypt(text, key)
        else:
            text = text.encode('utf-8')
            iv, ciphertext, tag = self._gcm_encrypt(key, text, self.__ass)
            return b64encode(iv + ciphertext + tag).decode('utf-8')

    def decrypt(self, text):
        '''对内容解密(默认)
        Args:
            text 字符串 需要解密内容
        Returns: 字符串 返回解密后的内容,解密失败返回None
        '''
        key = self.__key
        if self.__mode == 'ECB':
            return self._ecb_decrypt(text, key)
        else:
            text = b64decode(text)
            iv = text[0:12]
            tag = text[-16:]
            content = text[12:-16]
            return str(self._gcm_decrypt(key, self.__ass, iv, content, tag))

def test():
    aes = ZanthAES(mode='ECB')
    text = "32048319880206262X"
    result = aes.encrypt(text)
    print(result)
    print(aes.decrypt(result))

    pw = 'P2wQjONezpgsHlS3fH82tA=='
    ip = 'FefiwaUvyZXtzdxe2xWdOw=='
    print(aes.decrypt(pw))
    print(aes.decrypt(ip))

    ip = '120.78.189.52'
    pw = 's2e6LXfmEcd3$1dF'
    print(aes.encrypt(ip))
    print(aes.encrypt(pw))

    data = '{"UserName": "cy_rfid", "UserPassword": "cy_02024"}'
    aes.set_key('shinow90')
    print(aes.encrypt(data))

test()
