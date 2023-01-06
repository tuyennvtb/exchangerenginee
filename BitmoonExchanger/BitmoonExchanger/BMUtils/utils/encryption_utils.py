from Crypto.Cipher import AES
from base64 import b64encode, b64decode
class EncryptionUtils:
    def __init__(self):
        self.salt = '11mYzQnRx21HK664'
        self.enc_dec_method = 'utf-8'
        self.key="weAgupE4Hb4DcBXTQbG7wzneWAMNa32t"
    
    def encrypt(self,str_to_encrypt):
        try:
            aes_obj = AES.new(self.key.encode('utf8'), AES.MODE_CFB, self.salt.encode('utf8'))
            hx_enc = aes_obj.encrypt(str_to_encrypt.encode('utf8'))
            mret = b64encode(hx_enc).decode(self.enc_dec_method)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == 'IV must be 16 bytes long':
                raise ValueError('Encryption Error: SALT must be 16 characters long')
            elif value_error.args[0] == 'AES key must be either 16, 24, or 32 bytes long':
                raise ValueError('Encryption Error: Encryption key must be either 16, 24, or 32 characters long')
            else:
                raise ValueError(value_error)

    def decrypt(self, enc_str):
        try:
            aes_obj = AES.new(self.key.encode('utf8'), AES.MODE_CFB, self.salt.encode('utf8'))
            str_tmp = b64decode(enc_str.encode(self.enc_dec_method))
            str_dec = aes_obj.decrypt(str_tmp)
            mret = str_dec.decode(self.enc_dec_method)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == 'IV must be 16 bytes long':
                raise ValueError('Decryption Error: SALT must be 16 characters long')
            elif value_error.args[0] == 'AES key must be either 16, 24, or 32 bytes long':
                raise ValueError('Decryption Error: Encryption key must be either 16, 24, or 32 characters long')
            else:
                raise ValueError(value_error)

