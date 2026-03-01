from app.auth import verify_password

test_hash = '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC'
candidates = ['test123', 'password', '123456', 'admin', '1234', 'pass123', 'azerty', 'testtest', 'secret', 'maalem', 'artisan', 'hackathon', 'lm3alem', 'morocco', '000000', '111111']
for p in candidates:
    ok = verify_password(p, test_hash)
    if ok:
        print(f'FOUND PASSWORD: {p}')
        break
    print(f'{p}: wrong')
print('Done')
