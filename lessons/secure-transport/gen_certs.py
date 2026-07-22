"""
Week 12 lab -- certificate generator (init step).

Generates, at container startup, three things into a shared /certs volume:

  1. ca.crt / ca.key         -- a demo Certificate Authority (CA:TRUE).
  2. bob.crt / bob.key       -- Bob's server cert, CN=bob, SAN=DNS:bob,
                                SIGNED BY the demo CA. This is the legitimate
                                server identity.
  3. impostor.crt / impostor.key -- the MITM's cert. It ALSO claims CN=bob and
                                SAN=DNS:bob, but it is SELF-SIGNED -- there is
                                no CA signature over it. This is the whole
                                point of the lab: it looks like Bob by name,
                                but nothing a trusted authority vouches for
                                links it to Bob.

Nothing here is committed to the repo. Keys exist only inside the shared Docker
volume, are regenerated every run, and never touch the repository tree. (This
is why the compose files gate bob/mitm/alice on gen_certs completing first.)

The security property being demonstrated:
    openssl verify -CAfile ca.crt bob.crt        -> OK
    openssl verify -CAfile ca.crt impostor.crt   -> FAIL (self-signed)

A TLS client that loads ca.crt as its trust anchor and checks the chain will
accept bob.crt and REJECT impostor.crt. A client that skips that check
(CERT_NONE / check_hostname=False) accepts either one -- and that is the bug.
"""
import datetime
import os

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

CERT_DIR = os.environ.get("CERT_DIR", "/certs")
SERVER_NAME = os.environ.get("SERVER_NAME", "bob")


def _new_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _write_key(path: str, key: rsa.RSAPrivateKey) -> None:
    with open(path, "wb") as fh:
        fh.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )


def _write_cert(path: str, cert: x509.Certificate) -> None:
    with open(path, "wb") as fh:
        fh.write(cert.public_bytes(serialization.Encoding.PEM))


def build_ca() -> tuple[x509.Certificate, rsa.RSAPrivateKey]:
    key = _new_key()
    now = datetime.datetime.now(datetime.timezone.utc)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Week12 Demo CA")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)  # self-issued: a CA signs its own root cert
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=3650))
        # basicConstraints CA:TRUE -- this is what makes it a usable trust anchor.
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .sign(key, hashes.SHA256())
    )
    return cert, key


def build_server_cert_signed_by_ca(
    ca_cert: x509.Certificate, ca_key: rsa.RSAPrivateKey
) -> tuple[x509.Certificate, rsa.RSAPrivateKey]:
    """Bob's real cert: CN=bob, SAN=DNS:bob, signed BY the demo CA."""
    key = _new_key()
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, SERVER_NAME)]))
        .issuer_name(ca_cert.subject)  # issued by the CA, not self-issued
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(SERVER_NAME)]), critical=False
        )
        .sign(ca_key, hashes.SHA256())  # <-- signed by the CA's private key
    )
    return cert, key


def build_impostor_self_signed() -> tuple[x509.Certificate, rsa.RSAPrivateKey]:
    """The MITM's cert: ALSO claims CN=bob / SAN=DNS:bob, but self-signed --
    no CA vouches for it. A client that validates the chain rejects it; a
    client that skips validation accepts it (the bug)."""
    key = _new_key()
    now = datetime.datetime.now(datetime.timezone.utc)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, SERVER_NAME)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)  # self-issued: issuer == subject, no external signer
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        # Deliberately SAME name/SAN as Bob so the ONLY thing distinguishing
        # this cert from Bob's is the missing CA signature -- which is exactly
        # the property the lesson turns on.
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(SERVER_NAME)]), critical=False
        )
        .sign(key, hashes.SHA256())  # <-- signed by ITS OWN key, not the CA's
    )
    return cert, key


def main() -> None:
    os.makedirs(CERT_DIR, exist_ok=True)

    ca_cert, ca_key = build_ca()
    _write_cert(os.path.join(CERT_DIR, "ca.crt"), ca_cert)
    _write_key(os.path.join(CERT_DIR, "ca.key"), ca_key)

    bob_cert, bob_key = build_server_cert_signed_by_ca(ca_cert, ca_key)
    _write_cert(os.path.join(CERT_DIR, "bob.crt"), bob_cert)
    _write_key(os.path.join(CERT_DIR, "bob.key"), bob_key)

    imp_cert, imp_key = build_impostor_self_signed()
    _write_cert(os.path.join(CERT_DIR, "impostor.crt"), imp_cert)
    _write_key(os.path.join(CERT_DIR, "impostor.key"), imp_key)

    print(
        f"GEN_CERTS: wrote ca.crt, bob.crt (CN={SERVER_NAME}, signed by CA), "
        f"impostor.crt (CN={SERVER_NAME}, self-signed) to {CERT_DIR}",
        flush=True,
    )


if __name__ == "__main__":
    main()
