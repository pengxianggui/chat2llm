import base64
import time
from ctypes import Array
from http.client import HTTPException

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from configs import API_TOKEN_KEY
from server.db.models.client_model import ClientModel
from server.db.repository import get_client, get_client_secret


# 加密参数, 先通过client_id的公钥加密"client_id|user_id|username"字符串得到字符串encrypt_token, 再通过base64加密"client_id|encrypt_token",
# 得到token并返回
def encrypt(client_id, user_id, username):
    client: ClientModel = get_client(client_id)
    if client is None:
        raise HTTPException(status_code=500, detail="client_id not exist: " + client_id)

    timestamp = time.time()  # 秒级
    encrypt_token = rsa_encrypt(str(client_id) + "|" + user_id + "|" + username + "|" + str(timestamp), client.client_key)
    a = base64.b64encode(encrypt_token).decode()
    b = base64.b64encode((str(client_id) + "|" + a).encode()).decode()
    return b


# 解密token。 1. 先通过base64解密得到client_id和encrypt_token, 再通过client_id找到密钥, 通过密钥RSA解密encrypt_token,
# 得到client_id、user_id、username、timestamp
def decrypt(token):
    base64_decoded_token = base64.b64decode(token).decode()
    arr: Array = base64_decoded_token.split("|")
    if len(arr) != 2:
        raise HTTPException(status_code=401, detail=f"Authentication required: {API_TOKEN_KEY}无效!")

    client_id = arr[0]
    key, secret, enable = get_client_secret(client_id)
    if key is None:
        raise HTTPException(status_code=401,
                            detail=f"Authentication required: {API_TOKEN_KEY}无效!")

    encrypt_token = base64.b64decode(arr[1].encode())
    clear_text = rsa_decrypt(encrypt_token, secret)
    params = clear_text.split("|")

    if len(params) != 4:
        raise HTTPException(status_code=401,
                            detail=f"Authentication required: {API_TOKEN_KEY}无效!")

    return params[0], params[1], params[2], float(params[3])


# 加密。传入明文和公钥，返回加密密文
def rsa_encrypt(text: str, public_key: str) -> bytes:
    pk = serialization.load_pem_public_key(
        data=public_key.encode(),
        backend=default_backend()
    )
    ciphertext = pk.encrypt(
        text.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext


# RSA解密。传入加密密文和私钥，返回明文
def rsa_decrypt(ciphertext: bytes, private_key: str) -> str:
    pk = serialization.load_pem_private_key(
        data=private_key.encode(),
        password=None,
        backend=default_backend()
    )
    decrypted_text = pk.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_text.decode()


# 生成 RSA 密钥对
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        # key_size=2048,
        key_size=1024,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # 将私钥和公钥序列化为 PEM 格式字符串
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode(), public_pem.decode()
