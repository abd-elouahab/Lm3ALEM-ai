from app.ai.price_model import predict

tests = [
    ('zlayji',      4, 0.5,  'moyenne', 1, 'agadir'),
    ('zlayji',      2, 2.0,  'simple',  1, 'agadir'),
    ('sebbagh',     3, 5.0,  'simple',  1, 'agadir'),
    ('plombier',    3, 0.1,  'simple',  1, 'agadir'),
    ('electricien', 5, 0.01, 'moyenne', 2, 'agadir'),
    ('electricien', 3, 0.01, 'simple',  1, 'agadir'),
    ('gebbas',      2, 1.0,  'simple',  1, 'agadir'),
]
for args in tests:
    r = predict(*args)
    print(f"{args[0]:12} sev={args[1]} surf={args[2]}m2 {args[3]:8} => {r['price']:5} MAD, {r['duration_hours']}h")
