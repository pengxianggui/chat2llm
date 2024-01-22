from server.auth import generate_rsa_keys


# 生成密钥对
def test_generate_rsa_keys():
    key, secret = generate_rsa_keys()
    print(key)
    print(secret)
