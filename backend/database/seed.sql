SET client_encoding TO 'UTF8';

-- Clean slate
DELETE FROM artisans;
DELETE FROM clients;
DELETE FROM ratings;
DELETE FROM payments;
DELETE FROM guarantees;
DELETE FROM matching_attempts;
DELETE FROM jobs;
DELETE FROM users;

-- Reset sequences
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE artisans_id_seq RESTART WITH 1;
ALTER SEQUENCE clients_id_seq RESTART WITH 1;

-- Insert artisan users (id 1-20)
INSERT INTO users (email, password_hash, role, full_name, phone) VALUES
('ahmed.zlayji@example.com',     '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Ahmed Amrani',      '+212612345601'),
('brahim.zlayji@example.com',    '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Brahim Tazi',       '+212612345602'),
('fatima.sebbagh@example.com',   '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Fatima Bennani',    '+212612345603'),
('khadija.sebbagh@example.com',  '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Khadija Idrissi',   '+212612345604'),
('mohamed.gebbas@example.com',   '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Mohamed El Fassi',  '+212612345605'),
('youssef.gebbas@example.com',   '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Youssef Chraibi',   '+212612345606'),
('hassan.plombier@example.com',  '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Hassan Bensouda',   '+212612345607'),
('omar.plombier@example.com',    '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Omar Alaoui',       '+212612345608'),
('khalid.electricien@example.com','$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC','artisan', 'Khalid Benjelloun', '+212612345609'),
('driss.electricien@example.com','$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Driss Tazi',        '+212612345610'),
('mustapha.zlayji@example.com',  '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Mustapha Berrada',  '+212612345611'),
('latifa.sebbagh@example.com',   '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Latifa Moussaoui',  '+212612345612'),
('abdel.gebbas@example.com',     '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Abdelkader Fassi',  '+212612345613'),
('rachid.plombier@example.com',  '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Rachid Bennani',    '+212612345614'),
('karim.electricien@example.com','$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Karim El Amrani',   '+212612345615'),
('jamal.zlayji@example.com',     '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Jamal Chraibi',     '+212612345616'),
('zineb.sebbagh@example.com',    '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Zineb Alaoui',      '+212612345617'),
('hamid.gebbas@example.com',     '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Hamid Bensouda',    '+212612345618'),
('nabil.plombier@example.com',   '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Nabil Idrissi',     '+212612345619'),
('tarik.electricien@example.com','$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'artisan', 'Tarik Benjelloun',  '+212612345620');

-- Insert artisan profiles (no French special characters in bio)
INSERT INTO artisans (user_id, specialty, city, latitude, longitude, is_available, ranking_score, bio) VALUES
(1,  'zlayji',     'agadir',      30.4278, -9.5981, true, 100, 'Maalem zlayji avec 15 ans experience. Zellige traditionnel.'),
(2,  'zlayji',     'inezgane',    30.3567, -9.5369, true, 95,  'Specialiste zellige et faience.'),
(3,  'sebbagh',    'ait_melloul', 30.3333, -9.5000, true, 100, 'Peintre en batiment, finitions soignees.'),
(4,  'sebbagh',    'tiznit',      29.6974, -9.7316, true, 88,  'Peinture interieure et exterieure.'),
(5,  'gebbas',     'taroudant',   30.4727, -8.8772, true, 92,  'Platrerie et faux plafonds.'),
(6,  'gebbas',     'biougra',     30.2167, -9.3667, true, 100, 'Gebbas et enduits decoratifs.'),
(7,  'plombier',   'chtouka',     30.0833, -9.4667, true, 97,  'Plomberie sanitaire et chauffage.'),
(8,  'plombier',   'massa',       30.0667, -9.6500, true, 90,  'Depannage et installations neuves.'),
(9,  'electricien','drarga',      30.4833, -9.7167, true, 100, 'Electricien agree, tableaux et normes.'),
(10, 'electricien','dcheira',     30.3833, -9.5167, true, 94,  'Installation electrique domestique.'),
(11, 'zlayji',     'agadir',      30.4280, -9.5970, true, 85,  'Pose de zellige et mosaique.'),
(12, 'sebbagh',    'inezgane',    30.3570, -9.5370, true, 91,  'Peinture et ravalement de facades.'),
(13, 'gebbas',     'ait_melloul', 30.3340, -9.5010, true, 87,  'Platrerie et enduits.'),
(14, 'plombier',   'tiznit',      29.6980, -9.7320, true, 93,  'Plomberie et canalisation.'),
(15, 'electricien','taroudant',   30.4730, -8.8780, true, 89,  'Electricite batiment et solaire.'),
(16, 'zlayji',     'biougra',     30.2170, -9.3670, true, 96,  'Zellige artisanal et carrelage.'),
(17, 'sebbagh',    'chtouka',     30.0840, -9.4670, true, 84,  'Peinture et revetements muraux.'),
(18, 'gebbas',     'massa',       30.0670, -9.6510, true, 98,  'Gebbas traditionnel et moderne.'),
(19, 'plombier',   'drarga',      30.4840, -9.7170, true, 86,  'Plomberie residentielle.'),
(20, 'electricien','dcheira',     30.3840, -9.5170, true, 99,  'Electricien industriel et domestique.');

-- Insert client users (id 21-25)
INSERT INTO users (email, password_hash, role, full_name, phone) VALUES
('client1@test.com', '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'client', 'Client Test',    '+212600000001'),
('client2@test.com', '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'client', 'Karima Essaidi', '+212600000002'),
('client3@test.com', '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'client', 'Omar Tazi',      '+212600000003'),
('client4@test.com', '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'client', 'Fatima Bennani', '+212600000004'),
('client5@test.com', '$2b$12$KaNuYm2KVdLXZN6HsZtmOeL76AEOngka8Oq4GcNed4ot.v3r0bemC', 'client', 'Samir Hassani',  '+212600000005');

-- Insert client profiles
INSERT INTO clients (user_id, city, latitude, longitude) VALUES
(21, 'agadir',      30.4278, -9.5981),
(22, 'inezgane',    30.3567, -9.5369),
(23, 'ait_melloul', 30.3333, -9.5000),
(24, 'tiznit',      29.6974, -9.7316),
(25, 'taroudant',   30.4727, -8.8772);

-- Verify
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'artisans', COUNT(*) FROM artisans
UNION ALL
SELECT 'clients', COUNT(*) FROM clients;
