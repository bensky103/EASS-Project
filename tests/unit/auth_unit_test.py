from auth_service.security import hash_password, verify_password

def test_hash_and_verify():
    pw = "s3cr3t"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)

