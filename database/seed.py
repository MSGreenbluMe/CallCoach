import json
from database.db import get_connection, init_db


def seed_achievements(conn):
    """Seed default achievements."""
    achievements = [
        ("Prvý hovor", "Dokončiť prvý tréningový hovor", "🎯", "first_call", "1", "milestone"),
        ("Perfekcionista", "Získať 100% na ľubovoľnom scenári", "⭐", "perfect_score", "100", "excellence"),
        ("Streak Master", "5 po sebe idúcich dní tréning", "🔥", "streak_days", "5", "consistency"),
        ("Empat roka", "Priemer empatie > 9.0 (min 10 hovorov)", "💚", "avg_empathy", "9.0", "skill"),
        ("Speed Demon", "Dokončiť scenár pod 50% času s >80%", "⚡", "speed_score", "80", "efficiency"),
        ("Polyglot", "Dokončiť scenáre v 3 rôznych jazykoch", "🌍", "unique_languages", "3", "diversity"),
        ("Kategória komplet", "Dokončiť všetky scenáre v jednej kategórii", "🏆", "category_complete", "1", "completionist"),
        ("Záchranár", "Zmeniť ANGRY zákazníka na spokojného", "🛟", "angry_to_happy", "1", "skill"),
        ("Sales Shark", "5x úspešný upsell", "🦈", "upsell_count", "5", "skill"),
        ("Iron Man", "10 hovorov v jednom dni", "💪", "daily_calls", "10", "endurance"),
        ("Comeback Kid", "Po neúspešnom hovore hneď úspešný", "🔄", "comeback", "1", "resilience"),
    ]

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM achievements")
    if cursor.fetchone()[0] > 0:
        return

    cursor.executemany(
        "INSERT INTO achievements (name, description, icon, condition_type, condition_value, category) VALUES (?, ?, ?, ?, ?, ?)",
        achievements,
    )


def seed_users(conn):
    """Seed demo users."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        return

    users = [
        ("Admin", "admin@callcoach.local", "admin", "Demo", None, 0, 1),
        ("Ján Manažér", "manager@callcoach.local", "manager", "Demo", None, 0, 1),
        ("Petra Agentová", "petra@callcoach.local", "agent", "Demo", None, 350, 2),
        ("Tomáš Novák", "tomas@callcoach.local", "agent", "Demo", None, 120, 1),
        ("Mária Kováčová", "maria@callcoach.local", "agent", "Demo", None, 580, 3),
    ]

    cursor.executemany(
        "INSERT INTO users (name, email, role, team, avatar_url, xp, level) VALUES (?, ?, ?, ?, ?, ?, ?)",
        users,
    )


def seed_scenarios(conn):
    """Seed 3 MVP demo scenarios."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM scenarios")
    if cursor.fetchone()[0] > 0:
        return

    # Scenario 1: Reklamácia — E-shop
    cursor.execute("""
        INSERT INTO scenarios (
            name, description, category, difficulty, language,
            estimated_duration_min, max_duration_min,
            persona_name, persona_background, persona_mood, persona_patience,
            persona_comm_style, persona_hidden_need,
            primary_goal, success_definition, fail_conditions,
            first_message, temperature, is_active, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Reklamácia poškodeného tovaru",
        "Zákazníčka Jana Nováková volá ohľadom práčky, ktorú si kúpila pred 14 dňami. Práčka nefunguje správne — odstreďovanie sa zastavuje v polovici cyklu. Je frustrovaná, pretože musí prať ručne.",
        "COMPLAINTS", 2, "cs", 8, 15,
        "Jana Nováková",
        "45 rokov, učiteľka na základnej škole. Kúpila si práčku Samsung EcoBubble pred 14 dňami v e-shope. Odstreďovanie sa zastavuje v polovici cyklu. Musí prať ručne, čo ju veľmi zaťažuje, pretože má dvoch malých detí.",
        "FRUSTRATED", 6,
        "Hovorí rýchlo, je nervózna ale slušná. Občas zopakuje problém, aby zdôraznila závažnosť. Očakáva rýchle riešenie.",
        "Nechce čakať na opravu 2-3 týždne. V skutočnosti by najradšej vymenila práčku za lepší model (aj s doplatkom), pretože stratila dôveru v tento model.",
        "Vyriešiť reklamáciu a ponúknuť výmenu za vyšší model",
        "Zákazníčka súhlasí s výmenou za vyšší model a je spokojná s riešením",
        "Zákazníčka žiada vedúceho / zákazníčka zavesí nahnevaná / agent nesplní povinné body",
        "Dobrý deň, volám ohľadom objednávky číslo 2024-8847. Kúpila som si u vás práčku pred dvomi týždňami a mám s ňou vážny problém.",
        0.7, 1, 1,
    ))
    scenario1_id = cursor.lastrowid

    checkpoints_1 = [
        (scenario1_id, "Pozdrav a predstavenie sa", "Agent sa predstaví menom a názvom spoločnosti", 1, True, "Agent sa predstaví menom a privíta zákazníčku"),
        (scenario1_id, "Overenie identity zákazníka", "Agent si vyžiada meno a číslo objednávky", 2, True, "Agent overí identitu — meno alebo číslo objednávky"),
        (scenario1_id, "Aktívne vypočutie problému", "Agent nechá zákazníčku opísať problém bez prerušovania", 3, True, "Agent aktívne počúva, kladie doplňujúce otázky"),
        (scenario1_id, "Empatické vyjadrenie porozumenia", "Agent prejaví pochopenie situácie", 4, True, "Agent vyjadrí empatiu — chápe frustráciu, ospravedlní sa za nepríjemnosti"),
        (scenario1_id, "Zistenie detailov problému", "Agent sa pýta na konkrétne detaily poruchy", 5, False, "Agent sa pýta na detaily — kedy sa to stalo, ako často, aký program"),
        (scenario1_id, "Navrhnutie riešenia", "Agent ponúkne konkrétne riešenie (výmena/oprava)", 6, True, "Agent navrhne riešenie — výmenu, opravu alebo vrátenie peňazí"),
        (scenario1_id, "Potvrdenie súhlasu zákazníka", "Agent si overí, či zákazníčka súhlasí s riešením", 7, True, "Zákazníčka súhlasí s navrhnutým riešením"),
        (scenario1_id, "Zhrnutie dohodnutých krokov", "Agent zhrnie čo sa dohodli a aké budú ďalšie kroky", 8, True, "Agent zhrnie — čo sa stane ďalej, kedy, ako"),
        (scenario1_id, "Profesionálne rozlúčenie", "Agent sa profesionálne rozlúči", 9, True, "Agent sa rozlúči profesionálne a príjemne"),
    ]

    cursor.executemany(
        "INSERT INTO checkpoints (scenario_id, name, description, order_index, is_order_strict, detection_hint) VALUES (?, ?, ?, ?, ?, ?)",
        checkpoints_1,
    )

    # Scenario 2: Retencia — Telko
    cursor.execute("""
        INSERT INTO scenarios (
            name, description, category, difficulty, language,
            estimated_duration_min, max_duration_min,
            persona_name, persona_background, persona_mood, persona_patience,
            persona_comm_style, persona_hidden_need,
            primary_goal, success_definition, fail_conditions,
            first_message, temperature, is_active, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Retencia — Zrušenie zmluvy",
        "Zákazník Martin Horák volá, pretože chce zrušiť svoju telekomunikačnú zmluvu. Našiel lacnejšiu ponuku u konkurencie. Je pokojný ale rozhodnutý odísť.",
        "RETENTION", 4, "cs", 10, 15,
        "Martin Horák",
        "32 rokov, programátor. Zákazníkom operátora je 3 roky. Platí 599 Kč/mesiac za tarif s 5GB dát. Konkurencia ponúka 10GB za 449 Kč. Je technicky zdatný, argumentuje racionálne.",
        "CALM", 7,
        "Hovorí kľudne a vecne. Má jasné argumenty a čísla. Nenechá sa ľahko zviesť emóciami, chce fakty. Je ochotný počúvať, ale ak ponuka nebude dobrá, odíde.",
        "V skutočnosti nechce meniť operátora (má tam celú rodinu). Chce len lepšiu cenu a viac dát. Ak dostane porovnateľnú ponuku, zostane.",
        "Udržať zákazníka — ponúknuť lepší tarif alebo zľavu",
        "Zákazník súhlasí s novou ponukou a zostáva",
        "Zákazník trvá na zrušení / agent je agresívny / agent neponúkne žiadnu alternatívu",
        "Dobrý deň, volám preto, že by som chcel zrušiť svoju zmluvu. Moje zákaznícke číslo je 7742819.",
        0.7, 1, 1,
    ))
    scenario2_id = cursor.lastrowid

    checkpoints_2 = [
        (scenario2_id, "Pozdrav a predstavenie sa", "Agent sa predstaví a privíta zákazníka", 1, True, "Agent sa predstaví menom"),
        (scenario2_id, "Overenie identity", "Agent overí zákaznícke číslo alebo údaje", 2, True, "Agent overí identitu — zákaznícke číslo alebo meno"),
        (scenario2_id, "Zistenie dôvodu odchodu", "Agent sa pýta prečo chce zákazník odísť", 3, True, "Agent sa pýta na dôvod — prečo chce zrušiť zmluvu"),
        (scenario2_id, "Empatia a pochopenie", "Agent prejaví porozumenie pre zákazníkovu situáciu", 4, True, "Agent vyjadrí pochopenie — rozumie, chápe jeho pohľad"),
        (scenario2_id, "Protiponuka", "Agent ponúkne lepší tarif alebo zľavu", 5, True, "Agent ponúkne alternatívu — lepší tarif, zľavu, bonus"),
        (scenario2_id, "Handling námietok", "Agent reaguje na námietky zákazníka k ponuke", 6, False, "Agent reaguje na námietky — vysvetlí výhody, porovná"),
        (scenario2_id, "Dohodnutie výsledku", "Agent a zákazník sa dohodnú na ďalšom postupe", 7, True, "Dohoda o výsledku — zákazník zostáva alebo odchádza"),
        (scenario2_id, "Zhrnutie", "Agent zhrnie dohodnuté podmienky", 8, True, "Agent zhrnie čo sa dohodli"),
        (scenario2_id, "Rozlúčenie", "Profesionálne ukončenie hovoru", 9, True, "Agent sa rozlúči profesionálne"),
    ]

    cursor.executemany(
        "INSERT INTO checkpoints (scenario_id, name, description, order_index, is_order_strict, detection_hint) VALUES (?, ?, ?, ?, ?, ?)",
        checkpoints_2,
    )

    # Scenario 3: Tech Support — SW produkt
    cursor.execute("""
        INSERT INTO scenarios (
            name, description, category, difficulty, language,
            estimated_duration_min, max_duration_min,
            persona_name, persona_background, persona_mood, persona_patience,
            persona_comm_style, persona_hidden_need,
            primary_goal, success_definition, fail_conditions,
            first_message, temperature, is_active, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Tech Support — Prihlásenie do aplikácie",
        "Zákazníčka Eva Malá volá, pretože sa nedokáže prihlásiť do účtovnej aplikácie. Je zmätená a trochu nervózna z technológií. Potrebuje trpezlivého sprievodcu.",
        "TECH_SUPPORT", 3, "cs", 7, 12,
        "Eva Malá",
        "58 rokov, účtovníčka v malej firme. Používa účtovnú aplikáciu FakturaPro už 2 roky. Dnes ráno sa nemôže prihlásiť — aplikácia hlási 'Nesprávne heslo'. Skúšala to 5x. Bojí sa, že stratila dáta.",
        "CONFUSED", 8,
        "Hovorí pomaly, opatrne. Často sa ospravedlňuje, že nie je technicky zdatná. Potrebuje jednoduché inštrukcie krok za krokom. Ak agent použije odborné termíny, stratí sa.",
        "Má strach z technológií a bojí sa, že urobí niečo zle. Potrebuje nielen technické riešenie, ale aj uistenie, že jej dáta sú v bezpečí a že to zvládne.",
        "Vyriešiť problém s prihlásením a naučiť zákazníčku resetovať heslo",
        "Zákazníčka sa úspešne prihlási a vie ako si v budúcnosti resetovať heslo",
        "Zákazníčka nerozumie inštrukciám / agent je netrpezlivý / problém nie je vyriešený",
        "Dobrý deň, ja... ehm, ja volám, lebo sa nemôžem dostať do tej mojej aplikácie. Viete, tej na faktúry. Skúšam to už od rána a stále mi to píše nesprávne heslo.",
        0.8, 1, 1,
    ))
    scenario3_id = cursor.lastrowid

    checkpoints_3 = [
        (scenario3_id, "Pozdrav a predstavenie sa", "Agent sa predstaví a privíta zákazníčku", 1, True, "Agent sa predstaví menom a privíta"),
        (scenario3_id, "Overenie identity", "Agent overí meno a účet zákazníčky", 2, True, "Agent overí identitu — meno, email alebo ID účtu"),
        (scenario3_id, "Popis problému", "Agent nechá zákazníčku opísať problém vlastnými slovami", 3, True, "Agent počúva popis problému — čo sa deje, aká chybová hláška"),
        (scenario3_id, "Upokojenie zákazníčky", "Agent uistí zákazníčku, že dáta sú v bezpečí", 4, True, "Agent upokojí — dáta sú bezpečne uložené, žiadny strach"),
        (scenario3_id, "Krokový návod na reset hesla", "Agent prevedie zákazníčku krok za krokom procesom resetu hesla", 5, True, "Agent dáva jasné kroky — krok 1, krok 2, overuje pochopenie"),
        (scenario3_id, "Overenie funkčnosti", "Agent sa uistí, že sa zákazníčka úspešne prihlásila", 6, True, "Agent overí — prihlásilo sa to? Vidí svoje dáta?"),
        (scenario3_id, "Zhrnutie a tip do budúcna", "Agent zhrnie postup a poradí ako postupovať nabudúce", 7, True, "Agent zhrnie — ako si zapamätať heslo, čo robiť nabudúce"),
        (scenario3_id, "Rozlúčenie", "Profesionálne a priateľské rozlúčenie", 8, True, "Agent sa rozlúči priateľsky a profesionálne"),
    ]

    cursor.executemany(
        "INSERT INTO checkpoints (scenario_id, name, description, order_index, is_order_strict, detection_hint) VALUES (?, ?, ?, ?, ?, ?)",
        checkpoints_3,
    )


def seed_all():
    """Run all seed functions."""
    init_db()
    conn = get_connection()
    try:
        seed_users(conn)
        seed_scenarios(conn)
        seed_achievements(conn)
        conn.commit()
        print("Seed data inserted successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed_all()
