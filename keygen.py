from umbral import PublicKey, SecretKey
import base64

alices_secret_key = SecretKey.random()
alices_public_key = alices_secret_key.public_key()

serialized_public_key = base64.b64encode(bytes(alices_public_key)).decode('utf-8')
serialized_private_key = base64.b64encode(bytes(alices_secret_key)).decode('utf-8')

print("Public Key: " + serialized_public_key)
print("Private Key: " + serialized_private_key)