import sqlite3

def add_sample_challenge():
    # نام فایل دیتابیست را اینجا چک کن (معمولا users.db)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    try:
        # درج یک چالش نمونه
        c.execute("""
            INSERT INTO challenges (
                name, 
                description, 
                visibility, 
                status, 
                duration_days, 
                max_members, 
                requires_proof, 
                checkin_method, 
                goal_type, 
                tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'Free Smoke',            # name
            'Dont use Smoke', # description
            'Private',                       # visibility
            'Active',                       # status
            60,                             # duration_days
            100,                             # max_members
            1,                              # requires_proof (1 = True)
            'Photo',                        # checkin_method
            'Daily',                        # goal_type
            'Learning'                    # tags
        ))

        challenge_id = c.lastrowid
        conn.commit()
        print(f"✅ Challenge created successfully with ID: {challenge_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_sample_challenge()
