from razu.s3storage import S3Storage
import os
import sys
import hashlib
import shutil

# --- configuratie ---
BUCKET = 'context'
NAS_PATH = '/mnt/nas/edepot'
# --- einde configuratie ---

# dit python-script upload alle bestanden in de map generated naar de 'context' bucket


def _md5_hex(file_path: str) -> str:
    """Calculate MD5 hex digest of a file (for upload verification)."""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def upload_rdf_to_context(prefix: str = "") -> int:
    """
    Upload all files from the project's generated/ directory to the 'context' bucket using S3Storage.

    - Bucket: context
    - Object key: <prefix><filename> (default prefix '')
    - Minimal metadata is added for provenance.

    Returns process exit code (0 = success, 1 = failures occurred).
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    generated_dir = os.path.join(project_root, 'generated')

    if not os.path.isdir(generated_dir):
        print(f"ERROR: Generated directory not found: {generated_dir}", file=sys.stderr)
        return 1

    storage = S3Storage()

    # Ensure bucket exists
    bucket = BUCKET
    ok = False
    try:
        if hasattr(storage, 'check_or_create_bucket'):
            ok = storage.check_or_create_bucket(bucket)
        else:
            ok = True
    except Exception as e:
        print(f"ERROR: Failed to ensure bucket '{bucket}': {e}", file=sys.stderr)
        return 1

    if not ok:
        print(f"ERROR: Bucket '{bucket}' is not available.", file=sys.stderr)
        return 1

    failures = 0
    total = 0

    for name in sorted(os.listdir(generated_dir)):
        path = os.path.join(generated_dir, name)
        if not os.path.isfile(path):
            continue

        total += 1
        object_key = f"{prefix}{name}"

        metadata = {
            "project": "RAZU-thesauri",
            "source": "rdf",
            "filename": name,
        }

        try:
            local_md5 = _md5_hex(path)
            # store_file(bucket_name, object_key, local_filename, metadata)
            storage.store_file(bucket, object_key, path, metadata)

            if hasattr(storage, 'verify_upload'):
                storage.verify_upload(bucket, object_key, local_md5)
            # Ensure public readability
            if hasattr(storage, 'update_acl'):
                storage.update_acl(bucket, object_key, 'public-read')
            print(f"[OK] {path} -> s3://{bucket}/{object_key}")
        except Exception as e:
            failures += 1
            print(f"[FAIL] {path}: {e}", file=sys.stderr)

    print(f"Uploaded: {total - failures}, Failed: {failures}, Total: {total}")

    nas_dest = os.path.join(NAS_PATH, bucket)
    if not os.path.isdir(NAS_PATH):
        print(f"WAARSCHUWING: NAS-map niet beschikbaar: {NAS_PATH}", file=sys.stderr)
    else:
        os.makedirs(nas_dest, exist_ok=True)
        nas_failures = 0
        for name in sorted(os.listdir(generated_dir)):
            src = os.path.join(generated_dir, name)
            if not os.path.isfile(src):
                continue
            try:
                shutil.copy2(src, os.path.join(nas_dest, name))
                print(f"[NAS] {src} -> {nas_dest}/{name}")
            except Exception as e:
                nas_failures += 1
                print(f"[NAS FAIL] {src}: {e}", file=sys.stderr)
        if nas_failures:
            print(f"NAS-kopie: {nas_failures} fout(en)", file=sys.stderr)

    return 0 if failures == 0 else 1


if __name__ == '__main__':
    sys.exit(upload_rdf_to_context())
