import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'idv_master.db')

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# --- 1. テーブルの作成 (リセット) ---
# NOTE: 開発中はリセットしていますが、公開時には不要です。
cursor.executescript('''
    DROP TABLE IF EXISTS m_survivors;
    DROP TABLE IF EXISTS m_hunters;
    DROP TABLE IF EXISTS battle_records;
    DROP TABLE IF EXISTS battle_bans;
    DROP TABLE IF EXISTS feedbacks; -- ★案② 追加

    -- サバイバーマスタ
    CREATE TABLE m_survivors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        display_name TEXT NOT NULL,
        image_url TEXT
    );

    -- ハンターマスタ
    CREATE TABLE m_hunters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        display_name TEXT NOT NULL,
        image_url TEXT
    );

    -- 戦績テーブル
    CREATE TABLE battle_records (
        id TEXT PRIMARY KEY,
        hunter_id INTEGER NOT NULL,
        rank_tier TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hunter_id) REFERENCES m_hunters(id)
    );

    -- BAN詳細テーブル
    CREATE TABLE battle_bans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        battle_id TEXT NOT NULL,
        survivor_id INTEGER NOT NULL,
        FOREIGN KEY (battle_id) REFERENCES battle_records(id),
        FOREIGN KEY (survivor_id) REFERENCES m_survivors(id)
    );
    
    -- ★案② コメントテーブルの追加
    CREATE TABLE feedbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
''')

# --- 2. マスタデータの定義 (最新版) ---

survivors_data = [
    ('lucky_guy', '幸運児'), ('doctor', '医師'), ('lawyer', '弁護士'), ('thief', '泥棒'), 
    ('gardener', '庭師'), ('magician', 'マジシャン'), ('explorer', '冒険家'), ('mercenary', '傭兵'), 
    ('priestess', '祭司'), ('coordinator', '空軍'), ('mechanic', '機械技師'), ('forward', 'オフェンス'), 
    ('the_mind_s_eye', '心眼'), ('perfumer', '調香師'), ('cowboy', 'カウボーイ'), ('dancer', '踊り子'), 
    ('seer', '占い師'), ('embalmer', '納棺師'), ('prospector', '探鉱者'), ('enchantress', '呪術師'), 
    ('wildling', '野人'), ('acrobat', '曲芸師'), ('first_officer', '一等航海士'), ('barmaid', 'バーメイド'), 
    ('postman', 'ポストマン'), ('grave_keeper', '墓守'), ('prisoner', '「囚人」'), ('entomologist', '昆虫学者'), 
    ('painter', '画家'), ('batter', 'バッツマン'), ('toy_merchant', '玩具職人'), ('patient', '患者'), 
    ('psychologist', '「心理学者」'), ('novelist', '小説家'), ('little_girl', '「少女」'), ('weeping_clown', '泣きピエロ'), 
    ('professor', '教授'), ('antiquarian', '骨董商'), ('composer', '作曲家'), ('journalist', '記者'), 
    ('aeroplanist', '航空エンジニア'), ('cheerleader', '応援団'), ('puppeteer', '人形師'), ('fire_investigator', '火災調査員'), 
    ('faro_lady', '「レディ・ファウロ」'), ('knight', '「騎士」'), ('meteorologist', '気象学者'), ('archer', '弓使い'), 
    ('escape_master', '「脱出マスター」'), ('magic_lanternist', '幻灯師')
]

hunters_data = [
    ('hell_ember', '復讐者'), ('smiley_face', '道化師'), ('gamekeeper', '断罪狩人'), ('ripper', 'リッパー'), 
    ('soul_weaver', '結魂者'), ('geisha', '芸者'), ('wu_chang', '白黒無常'), ('photographer', '写真家'), 
    ('mad_eyes', '狂眼'), ('feaster', '黄衣の王'), ('dream_witch', '夢の魔女'), ('axe_boy', '泣き虫'), 
    ('evil_reptilian', '魔トカゲ'), ('bloody_queen', '血の女王'), ('guard_26', 'ガードNo.26'), ('disciple', '「使徒」'), 
    ('violinist', 'ヴァイオリニスト'), ('sculptor', '彫刻師'), ('undead', 'アンデッド'), ('breaking_wheel', '破輪'), 
    ('naiad', '漁師'), ('wax_artist', '蝋人形師'), ('nightmare', '「悪夢」'), ('clerk', '書記官'), 
    ('hermit', '隠者'), ('night_watch', '夜の番人'), ('opera_singer', 'オペラ歌手'), ('fool_s_gold', '「フールズ・ゴールド」'), 
    ('ivy', '時空の影'), ('goatman', '「足萎えの羊」'), ('hullabaloo', '「フラバルー」'), ('general_merchant', '雑貨商'), 
    ('billiard_player', '「ビリヤードプレイヤー」'), ('queen_bee', '「女王蜂」')
]

# --- 3. データの挿入 ---
cursor.executemany('INSERT INTO m_survivors (name, display_name) VALUES (?, ?)', survivors_data)
cursor.executemany('INSERT INTO m_hunters (name, display_name) VALUES (?, ?)', hunters_data)

print(f"マスタデータ（サバイバー:{len(survivors_data)}体, ハンター:{len(hunters_data)}体）の作成完了！")

connection.commit()
connection.close()