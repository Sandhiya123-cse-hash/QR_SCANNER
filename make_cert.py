import sys
import ipaddress
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


if len(sys.argv) != 2:
    print("Usage: python make_cert.py LAPTOP_IP")
    sys.exit(1)

laptop_ip = ipaddress.ip_address(sys.argv[1])

# Create local certificate authority
ca_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

ca_name = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "RotationQR Local CA")
])

now = datetime.utcnow()

ca_cert = (
    x509.CertificateBuilder()
    .subject_name(ca_name)
    .issuer_name(ca_name)
    .public_key(ca_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(now - timedelta(days=1))
    .not_valid_after(now + timedelta(days=3650))
    .add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True
    )
    .sign(ca_key, hashes.SHA256())
)

# Save CA certificate and private key
with open("rootCA.pem", "wb") as f:
    f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

with open("rootCA.key", "wb") as f:
    f.write(ca_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ))

# Create server key
server_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

server_name = x509.Name([
    x509.NameAttribute(
        NameOID.COMMON_NAME,
        "RotationQR Local Server"
    )
])

# Certificate valid for localhost and laptop IP
san = x509.SubjectAlternativeName([
    x509.DNSName("localhost"),
    x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
    x509.IPAddress(laptop_ip)
])

server_cert = (
    x509.CertificateBuilder()
    .subject_name(server_name)
    .issuer_name(ca_name)
    .public_key(server_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(now - timedelta(days=1))
    .not_valid_after(now + timedelta(days=365))
    .add_extension(san, critical=False)
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True
    )
    .sign(ca_key, hashes.SHA256())
)

with open("cert.pem", "wb") as f:
    f.write(server_cert.public_bytes(serialization.Encoding.PEM))

with open("key.pem", "wb") as f:
    f.write(server_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    ))

print("Certificates created.")
print("Copy rootCA.pem to your phone and install it as a CA certificate.")
print("Keep rootCA.key private. Do not share it.")