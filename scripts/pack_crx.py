"""Signs the release zip as a CRX3 package and writes the Edge/Chrome update manifest.

Uses only the Python standard library and the `openssl` command (built into
GitHub's Ubuntu runners and Git for Windows), so no third-party packages.

    # Print the extension ID for a signing key (the ID never changes for a key):
    python scripts/pack_crx.py --key key.pem --print-id

    # Sign a zip and write updates.xml (done by the release workflow):
    python scripts/pack_crx.py --key key.pem --zip in.zip --crx out.crx \
        --updates-xml updates.xml --version 1.2.0 --codebase https://.../out.crx

    # Check a .crx's structure and signature:
    python scripts/pack_crx.py --verify out.crx

The private key is only ever passed to openssl by file path; it is never read,
printed or logged by this script.
"""

import argparse
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
from xml.sax.saxutils import quoteattr

MAGIC = b"Cr24"
SIGNED_DATA_PREFIX = b"CRX3 SignedData\x00"


def openssl(*args, data=None):
    try:
        return subprocess.run(["openssl", *args], input=data, capture_output=True, check=True).stdout
    except FileNotFoundError:
        sys.exit("openssl not found on PATH.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"openssl {args[0]} failed: {e.stderr.decode(errors='replace').strip()}")


def public_key_der(key_path):
    return openssl("pkey", "-in", key_path, "-pubout", "-outform", "DER")


def crx_id_bytes(pub_der):
    return hashlib.sha256(pub_der).digest()[:16]


def extension_id(pub_der):
    # Hex digits 0-f of the first 16 bytes of SHA-256(public key) mapped to a-p.
    return "".join(chr(ord("a") + int(c, 16)) for c in crx_id_bytes(pub_der).hex())


# --- Minimal protobuf encoding/decoding (only what CRX3 headers need) --------

def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def field(number, payload):
    # Length-delimited field (wire type 2).
    return varint((number << 3) | 2) + varint(len(payload)) + payload


def parse_fields(buf):
    i, fields = 0, []
    while i < len(buf):
        key, i = read_varint(buf, i)
        if key & 7 != 2:
            raise ValueError("unexpected wire type")
        length, i = read_varint(buf, i)
        fields.append((key >> 3, buf[i:i + length]))
        i += length
    return fields


def read_varint(buf, i):
    shift = n = 0
    while True:
        b = buf[i]
        i += 1
        n |= (b & 0x7F) << shift
        if not b & 0x80:
            return n, i
        shift += 7


# --- CRX3 --------------------------------------------------------------------

def sign(key_path, zip_bytes, pub_der):
    signed_data = field(1, crx_id_bytes(pub_der))  # SignedData { crx_id }
    message = SIGNED_DATA_PREFIX + struct.pack("<I", len(signed_data)) + signed_data + zip_bytes
    signature = openssl("dgst", "-sha256", "-sign", key_path, data=message)
    proof = field(1, pub_der) + field(2, signature)  # AsymmetricKeyProof
    header = field(2, proof) + field(10000, signed_data)  # CrxFileHeader
    return MAGIC + struct.pack("<II", 3, len(header)) + header + zip_bytes


def verify(crx_bytes):
    if crx_bytes[:4] != MAGIC or struct.unpack("<I", crx_bytes[4:8])[0] != 3:
        sys.exit("Not a CRX3 file.")
    header_len = struct.unpack("<I", crx_bytes[8:12])[0]
    header = crx_bytes[12:12 + header_len]
    zip_bytes = crx_bytes[12 + header_len:]
    fields = dict(parse_fields(header))
    signed_data = fields[10000]
    proof = dict(parse_fields(fields[2]))
    pub_der, signature = proof[1], proof[2]
    if dict(parse_fields(signed_data))[1] != crx_id_bytes(pub_der):
        sys.exit("CRX ID doesn't match the public key.")
    message = SIGNED_DATA_PREFIX + struct.pack("<I", len(signed_data)) + signed_data + zip_bytes
    with tempfile.TemporaryDirectory() as tmp:
        pub_path = os.path.join(tmp, "pub.der")
        sig_path = os.path.join(tmp, "sig.bin")
        with open(pub_path, "wb") as f:
            f.write(pub_der)
        with open(sig_path, "wb") as f:
            f.write(signature)
        openssl("dgst", "-sha256", "-verify", pub_path, "-keyform", "DER", "-signature", sig_path, data=message)
    if zip_bytes[:4] != b"PK\x03\x04":
        sys.exit("CRX payload is not a zip.")
    return extension_id(pub_der)


def updates_xml(ext_id, version, codebase):
    return (
        "<?xml version='1.0' encoding='UTF-8'?>\n"
        "<gupdate xmlns='http://www.google.com/update2/response' protocol='2.0'>\n"
        f"  <app appid={quoteattr(ext_id)}>\n"
        f"    <updatecheck codebase={quoteattr(codebase)} version={quoteattr(version)} />\n"
        "  </app>\n"
        "</gupdate>\n"
    )


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--key", help="PEM private key (PKCS#8 RSA)")
    p.add_argument("--print-id", action="store_true", help="print the extension ID for --key and exit")
    p.add_argument("--zip", help="extension zip to sign")
    p.add_argument("--crx", help="output .crx path")
    p.add_argument("--updates-xml", help="output update manifest path")
    p.add_argument("--version", help="extension version for updates.xml")
    p.add_argument("--codebase", help="download URL of the .crx for updates.xml")
    p.add_argument("--verify", metavar="CRX", help="verify a .crx and print its extension ID")
    a = p.parse_args()

    if a.verify:
        with open(a.verify, "rb") as f:
            print(f"Valid CRX3, signature OK. Extension ID: {verify(f.read())}")
        return

    if not a.key:
        p.error("--key is required")
    pub_der = public_key_der(a.key)
    ext_id = extension_id(pub_der)

    if a.print_id:
        print(ext_id)
        return

    if not (a.zip and a.crx):
        p.error("--zip and --crx are required to pack")
    with open(a.zip, "rb") as f:
        crx = sign(a.key, f.read(), pub_der)
    with open(a.crx, "wb") as f:
        f.write(crx)
    if verify(crx) != ext_id:
        sys.exit("Self-check failed: packed CRX doesn't verify.")
    print(f"Wrote {a.crx} (extension ID {ext_id})")

    if a.updates_xml:
        if not (a.version and a.codebase):
            p.error("--version and --codebase are required with --updates-xml")
        with open(a.updates_xml, "w", encoding="utf-8", newline="\n") as f:
            f.write(updates_xml(ext_id, a.version, a.codebase))
        print(f"Wrote {a.updates_xml}")


if __name__ == "__main__":
    main()
