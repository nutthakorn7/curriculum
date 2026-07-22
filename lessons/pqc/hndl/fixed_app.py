"""FIXED channel -- Week 15 PQC lab: Harvest Now, Decrypt Later, mitigated with a HYBRID KEM.

Same scenario as vulnerable_app.py, but the session key is derived from TWO independent shared
secrets combined in a KDF:

    session_key = KDF( s_classical  ||  s_pqc )

  * s_classical comes from the SAME small textbook-RSA KEM as the vulnerable app -- still breakable.
  * s_pqc comes from REAL ML-KEM-512 (NIST FIPS 203, via kyber-py) -- lattice-based, and its
    private decapsulation key is NEVER in the transcript.

This is exactly the "hybrid mode" arrow in the Week 15 quantum-readiness picture: deploy classical
+ PQC together so that breaking either one alone is not enough. An attacker who harvests this
transcript and later factors the small RSA modulus recovers s_classical -- but the KDF also needs
s_pqc, which requires the ML-KEM private key they do not have. KDF(s_classical || guess) != the
real key, so AES-GCM's auth tag fails and the flag stays confidential. The captured traffic is safe
as long as EITHER KEM holds.

Endpoints:
  GET /          -> description
  GET /capture   -> {n, e, kem_ct_c, ek, kem_ct_pq, aes_nonce, aes_ct}
                    (ek = ML-KEM PUBLIC key -- public by design; the private key is not here)
"""
import os

from flask import Flask, jsonify
from kyber_py.ml_kem import ML_KEM_512

import kemlib

app = Flask(__name__)
FLAG_HNDL = os.environ.get("FLAG_HNDL", "FLAG{harvest_now_decrypt_later}")


def _make_capture():
    n, e, _d = kemlib.gen_small_rsa()
    s_c, kem_ct_c = kemlib.rsa_encaps(n, e)
    ek, _dk = ML_KEM_512.keygen()             # ek public; _dk (private) is discarded, never sniffable
    s_pq, kem_ct_pq = ML_KEM_512.encaps(ek)
    session_key = kemlib.kdf(kemlib.classical_secret_bytes(s_c, n), s_pq)
    nonce, blob = kemlib.seal(session_key, FLAG_HNDL.encode())
    return {
        "n": n, "e": e, "kem_ct_c": kem_ct_c,
        "ek": ek.hex(), "kem_ct_pq": kem_ct_pq.hex(),
        "aes_nonce": nonce.hex(), "aes_ct": blob.hex(),
    }


CAPTURE = _make_capture()


@app.route("/")
def index():
    return (
        "Week 15 PQC lab -- Harvest Now, Decrypt Later (FIXED channel, HYBRID classical + ML-KEM).\n"
        "GET /capture; run exploit.py against this port and watch it break the classical half but\n"
        "fail to decrypt -- the ML-KEM half keeps the harvested capture confidential.\n"
    )


@app.route("/capture")
def capture():
    return jsonify(CAPTURE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8121)
