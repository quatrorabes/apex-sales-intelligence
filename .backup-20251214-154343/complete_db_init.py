def init_db():
    '''Initialize all database tables with enhanced schema'''
    with get_db() as conn:
        cursor = conn.cursor()

        # Create contacts table with ALL required columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hubspot_id VARCHAR(255),
                hs_object_id VARCHAR(255),
                name VARCHAR(255) NOT NULL,
                firstname VARCHAR(100),
                lastname VARCHAR(100),
                title VARCHAR(200),
                job_title VARCHAR(200),
                company VARCHAR(255),
                industry VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                linkedin_url VARCHAR(500),
                linkedin VARCHAR(500),
                profile_picture_url VARCHAR(500),
                lifecycle_stage VARCHAR(100),
                enrichment_status VARCHAR(50) DEFAULT 'pending',
                enriched_at TIMESTAMP,
                opportunity_score INTEGER DEFAULT 0,
                lead_tier VARCHAR(50),
                buyer_role VARCHAR(100),
                department VARCHAR(100),
                seniority VARCHAR(100),
                hubspot_owner VARCHAR(255),
                last_activity_date TIMESTAMP,
                location VARCHAR(200),
                website VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                tags TEXT,
                notes TEXT,
                source VARCHAR(100),
                campaign VARCHAR(200),
                lead_score INTEGER DEFAULT 0,
                engagement_score INTEGER DEFAULT 0,
                fit_score INTEGER DEFAULT 0,
                activity_score INTEGER DEFAULT 0,
                last_contacted TIMESTAMP,
                times_contacted INTEGER DEFAULT 0,
                last_email_opened TIMESTAMP,
                last_email_clicked TIMESTAMP,
                social_linkedin VARCHAR(500),
                social_twitter VARCHAR(500),

                -- Enrichment fields
                enrichment_data TEXT,
                pain_points TEXT,
                talking_points TEXT,
                myers_briggs VARCHAR(10),

                -- HubSpot sync
                hubspot_sync_status VARCHAR(50),
                hubspot_last_synced TIMESTAMP,
                hubspot_error TEXT
            )
        ''')

        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_enrichment_status ON contacts(enrichment_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_opportunity_score ON contacts(opportunity_score DESC)')

        conn.commit()
        print("✅ Database tables initialized with all columns")