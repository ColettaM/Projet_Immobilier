--Auteur: Coletta Moutsiha
--Date:11-Avril-2025
--###############################################################################
			--MODELE RELATIONNEL PROJET IMMO 
--###############################################################################

-- ========================
-- TABLE DES AGENTS IMMOBILIERS
-- ========================
CREATE TABLE agent (
    agent_id SERIAL PRIMARY KEY,  -- Identifiant unique de l'agent immobilier
    nom VARCHAR(50) NOT NULL,  -- Nom de l'agent
    prenom VARCHAR(50) NOT NULL,  -- Prénom de l'agent
    email VARCHAR(100) NOT NULL UNIQUE,  -- Email unique pour chaque agent
    telephone VARCHAR(20),  -- Numéro de téléphone de l'agent
    agence VARCHAR(50) NOT NULL,  -- Nom de l'agence immobilière
    code_postal_agence INTEGER NOT NULL,  -- Code postal de l'agence
    ville_agence VARCHAR(20) NOT NULL,  -- Ville de l'agence
    CONSTRAINT unique_nom_prenom_agent UNIQUE (nom, prenom, email)  
    -- Contrainte pour empêcher deux agents d'avoir le même nom,prénom et email);
);

-- ========================
-- TABLE DES VENDEURS
-- ========================
CREATE TABLE vendeur (
    vendeur_id SERIAL PRIMARY KEY,  -- Identifiant unique du vendeur
    nom VARCHAR(50) NOT NULL,  -- Nom du vendeur
    prenom VARCHAR(50) NOT NULL,  -- Prénom du vendeur
    email VARCHAR(100) NOT NULL UNIQUE,  -- Email unique pour chaque vendeur
    telephone VARCHAR(20),  -- Numéro de téléphone du vendeur
    code_postal INTEGER NOT NULL,  -- Code postal de l'emplacement du vendeur
    ville VARCHAR(20) NOT NULL,  -- Ville du vendeur
    CONSTRAINT unique_nom_prenom_vendeur UNIQUE (nom, prenom, email)  
    -- Contrainte pour empêcher deux vendeurs d'avoir le même nom,prénom et email
);

-- ========================
-- TABLE DES ACHETEURS
-- ========================
CREATE TABLE acheteur (
    acheteur_id SERIAL PRIMARY KEY,  -- Identifiant unique de l'acheteur
    nom VARCHAR(50) NOT NULL,  -- Nom de l'acheteur
    prenom VARCHAR(50) NOT NULL,  -- Prénom de l'acheteur
    email VARCHAR(100) NOT NULL UNIQUE,  -- Email unique pour chaque acheteur
    telephone VARCHAR(20),  -- Numéro de téléphone de l'acheteur
    code_postal INTEGER NOT NULL,  -- Code postal de l'emplacement de l'acheteur
    ville VARCHAR(20) NOT NULL,  -- Ville de l'acheteur
    CONSTRAINT unique_nom_prenom_acheteur UNIQUE (nom, prenom, email)  
    -- Contrainte pour empêcher deux acheteurs d'avoir le même nom,prénom et email
);


-- ========================
-- TABLE DES BIENS IMMOBILIERS
-- ========================
CREATE TABLE bien_immobilier (
    bien_id SERIAL PRIMARY KEY,  -- Identifiant unique du bien immobilier
    type_bien VARCHAR(50)NOT NULL CHECK (type_bien IN ( 'Appartement', 'maison', 'local commercial', 'bureau' )),
    categorie VARCHAR(10) NOT NULL CHECK (categorie IN ('vente','location' )),
    numero_voie VARCHAR(5) NOT NULL,  -- Numéro de la voie
    type_voie VARCHAR(10) NOT NULL,  -- Type de voie (rue, avenue, impasse, etc.)
    nom_voie VARCHAR(50) NOT NULL,  --  Libellé de la voie
    code_postal INTEGER NOT NULL,  -- Code postal de l'emplacement du bien
    ville VARCHAR(20) NOT NULL,  -- Ville ou se trouve le bien
    nb_pieces INTEGER NOT NULL,  -- Nombre de pieces dans le bien
    parking BOOLEAN DEFAULT FALSE, -- Indique si le bien dispose d'un parking
    balcon BOOLEAN DEFAULT FALSE,  -- Indique si le bien dispose d'un balcon
    ascenseur BOOLEAN DEFAULT FALSE,  -- Indique si le bien dispose d'un ascenseur
    jardin BOOLEAN DEFAULT FALSE, -- Indique si le bien dispose d'un jardin
    piscine BOOLEAN DEFAULT FALSE, -- Indique si le bien dispose d'une piscine
    superficie INTEGER NOT NULL,  -- Superficie en m²
    prix DECIMAL(10, 2) NOT NULL,  -- Prix du bien immobilier
    date_disponibilite DATE NOT NULL,
    descriptions TEXT,
    statut VARCHAR(20) NOT NULL CHECK (statut IN ('disponible', 'sous offre', 'vendu', 'loué', 'retiré')), -- Statut du bien
    url_wikipedia URL NOT NULL -- URL de la page Wikipedia du bien

); 

-- ========================
-- TABLE DE LIAISON ENTRE AGENTS ET VENDEURS
-- ========================
CREATE TABLE portefeuille_vendeur (
    portefeuille_vendeur_id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL,    -- Référence à l'agent
    vendeur_id INTEGER NOT NULL,  -- Référence au vendeur
    bien_id INTEGER NOT NULL UNIQUE,     -- Référence au bien 
    FOREIGN KEY (agent_id) REFERENCES agent(agent_id) ON DELETE CASCADE,
    FOREIGN KEY (vendeur_id) REFERENCES vendeur(vendeur_id) ON DELETE CASCADE,
    FOREIGN KEY (bien_id) REFERENCES bien_immobilier(bien_id) ON DELETE CASCADE,
);


-- ========================
-- TABLE DE LIAISON ENTRE AGENTS ET ACHETEURS
-- ========================
CREATE TABLE portefeuille_acheteur (
    portefeuille_acheteur_id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL,  
    acheteur_id INTEGER NOT NULL,  
    bien_id INTEGER NOT NULL,    
    FOREIGN KEY (agent_id) REFERENCES agent(agent_id) ON DELETE CASCADE,
    FOREIGN KEY (acheteur_id) REFERENCES acheteur(acheteur_id) ON DELETE CASCADE,
    FOREIGN KEY (bien_id) REFERENCES bien_immobilier(bien_id) ON DELETE CASCADE,
    UNIQUE (agent_id, acheteur_id, bien_id) -- Garantie d'unicité de la relation
);


-- ================================
-- TABLE DES SUIVIS BIENS-VENDEUR
-- ================================
CREATE TABLE suivi_bien_vendeur (
    suivi_bien_vendeur_id SERIAL PRIMARY KEY,
    pv_id INTEGER NOT NULL,
    canal VARCHAR(20) NOT NULL CHECK (canal IN ('rdv', 'email', 'appel', 'sms', 'autre')),
    etat_bien VARCHAR(30) NOT NULL CHECK (etat_bien IN ('prospection','estimation', 'signature du compromis', 'négociation', 'mise en vente', 'annulation', 'signature de la vente')),  --l'etat du bien
    date_suivi DATE NOT NULL, -- Date du suivi
    commentaire TEXT, -- Commentaires ou retours de l'acheteur sur le bien
    FOREIGN KEY (pv_id) REFERENCES portefeuille_vendeur(portefeuille_vendeur_id) ON DELETE CASCADE
);


-- =============================
-- TABLE DES SUIVIS BIENS-ACHETEUR
-- =============================
CREATE TABLE suivi_bien_acheteur (
    suivi_bien_acheteur_id SERIAL PRIMARY KEY,
    pa_id INTEGER NOT NULL,
    canal VARCHAR(20) NOT NULL CHECK (canal IN ('rdv', 'email', 'appel', 'sms', 'autre')), -- Canal de retour
    etat_bien VARCHAR(30) NOT NULL CHECK (etat_bien IN ('communiqué', 'visité', 'refusé', 'offre faite', 'offre acceptée', 'signature du compromis', 'négocié', 'annulé', 'acte final signé')), -- Statut du bien
    date_suivi DATE NOT NULL , -- Date du suivi
    feedback TEXT,  -- Commentaires ou retours de l'acheteur sur le bien
    FOREIGN KEY (pa_id) REFERENCES portefeuille_acheteur(portefeuille_acheteur_id) ON DELETE CASCADE
);


-- ========================
-- TABLE DES CRITÈRES DE RECHERCHE
-- ========================
CREATE TABLE critere (
    critere_id SERIAL PRIMARY KEY,  -- Identifiant unique des critères de recherche
    acheteur_id INTEGER NOT NULL UNIQUE,  -- Chaque acheteur a un seul ensemble de critères
    type_bien VARCHAR(50) NOT NULL CHECK (type_bien IN ('Appartement', 'maison', 'local commercial', 'bureau')),  -- Type de bien recherché
    categorie VARCHAR(10) NOT NULL CHECK (categorie IN ('vente', 'location')),  -- Catégorie de bien recherchée
    nb_pieces_min INTEGER NOT NULL,  -- Nombre minimal de pieces souhaitées
    nb_pieces_max INTEGER ,  -- Nombre maximal de pieces souhaitées
    superficie_min INTEGER NOT NULL,  -- Superficie minimale souhaitée
    superficie_max INTEGER,  -- Superficie maximale souhaitée
    budget_max DECIMAL NOT NULL,  -- Budget maximum de l'acheteur
    parking BOOLEAN DEFAULT FALSE, 
    balcon BOOLEAN DEFAULT FALSE, 
    ascenseur BOOLEAN DEFAULT FALSE, 
    jardin BOOLEAN DEFAULT FALSE,                                              
    piscine BOOLEAN DEFAULT FALSE,
    code_postal INTEGER NOT NULL,  -- Code postal de la zone recherchée
    ville VARCHAR(20) NOT NULL,  -- Ville préférée de l'acheteur  
    date_emmenagement DATE NOT NULL, -- Date d'emménagement souhaitée
    FOREIGN KEY (acheteur_id) REFERENCES acheteur(acheteur_id) ON DELETE CASCADE
);

