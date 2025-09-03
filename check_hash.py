import hashlib

password = "sergiosena"
sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
print(f"SHA256 hash: {sha256_hash}")

# Verificar se é igual ao que está no Secrets Manager
stored_hash = "320586432d7afc8f641e4763810881e8276831dc2d583ecdde92d4d9c5cdef73"
print(f"Stored hash: {stored_hash}")
print(f"Match: {sha256_hash == stored_hash}")