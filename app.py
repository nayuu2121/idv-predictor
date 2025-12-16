import os
import sqlite3
import uuid
from flask import Flask, render_template, request, g, redirect, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'idv_master.db')

app = Flask(__name__)

# --- DB接続処理 ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- 機能: 予測とデータ数チェック (案③) ---
def predict_hunter_stats(ban_ids):
    db = get_db()
    valid_ids = [bid for bid in ban_ids if bid]
    if not valid_ids: return [], 0

    placeholders = ','.join(['?'] * len(valid_ids))
    
    # 総データ数チェック（案③）
    count_query = f'''
        SELECT COUNT(DISTINCT br.id) as total
        FROM battle_records br
        JOIN battle_bans bb ON br.id = bb.battle_id
        WHERE bb.survivor_id IN ({placeholders})
    '''
    total_count = db.execute(count_query, valid_ids).fetchone()['total']

    # ランキング取得
    query = f'''
        SELECT h.display_name, COUNT(br.hunter_id) as count
        FROM battle_records br
        JOIN battle_bans bb ON br.id = bb.battle_id
        JOIN m_hunters h ON br.hunter_id = h.id
        WHERE bb.survivor_id IN ({placeholders})
        GROUP BY h.id, h.display_name
        ORDER BY count DESC LIMIT 5
    '''
    results = db.execute(query, valid_ids).fetchall()
    
    return results, total_count

# --- 機能: ハンター別BANランキング集計 (案① 詳細ページ用) ---
def get_hunter_ban_ranking():
    db = get_db()
    hunters = db.execute('SELECT id, display_name FROM m_hunters ORDER BY id').fetchall()
    return hunters

def get_stats_by_hunter(hunter_id):
    db = get_db()
    query = '''
        SELECT s.display_name, COUNT(bb.survivor_id) as count
        FROM battle_records br
        JOIN battle_bans bb ON br.id = bb.battle_id
        JOIN m_survivors s ON bb.survivor_id = s.id
        WHERE br.hunter_id = ?
        GROUP BY s.id, s.display_name
        ORDER BY count DESC
        LIMIT 10
    '''
    return db.execute(query, (hunter_id,)).fetchall()

# --- 機能: データ登録 ---
def register_battle_result(ban_ids, hunter_id):
    db = get_db()
    battle_id = str(uuid.uuid4())
    try:
        db.execute('INSERT INTO battle_records (id, hunter_id) VALUES (?, ?)', (battle_id, hunter_id))
        valid_ids = [bid for bid in ban_ids if bid]
        for survivor_id in valid_ids:
            db.execute('INSERT INTO battle_bans (battle_id, survivor_id) VALUES (?, ?)', (battle_id, survivor_id))
        db.commit()
        return True
    except Exception as e:
        print(f"Error registering battle: {e}")
        db.rollback()
        return False

# --- 機能: コメント登録 (案②) ---
def register_feedback(content):
    db = get_db()
    try:
        db.execute('INSERT INTO feedbacks (content) VALUES (?)', (content,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error registering feedback: {e}")
        return False

# --- ルーティング ---

@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    survivors = db.execute('SELECT id, display_name FROM m_survivors ORDER BY id').fetchall()
    hunters = db.execute('SELECT id, display_name FROM m_hunters ORDER BY id').fetchall()
    
    prediction_result = []
    total_samples = 0
    selected_bans = ['', '', '', '']
    message = None

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'predict':
            selected_bans = [request.form.get(f'ban{i+1}') for i in range(4)]
            prediction_result, total_samples = predict_hunter_stats(selected_bans)
            
        elif action == 'register':
            selected_bans = [request.form.get(f'ban{i+1}') for i in range(4)]
            actual_hunter = request.form.get('actual_hunter')
            if actual_hunter and any(selected_bans):
                register_battle_result(selected_bans, actual_hunter)
                message = "✅ データ登録ありがとうございます！"
                selected_bans = ['', '', '', '']
                
        elif action == 'feedback':
            content = request.form.get('content')
            if content:
                register_feedback(content)
                message = "📩 ご意見ありがとうございます！開発の励みになります。"

    return render_template('index.html', 
                           survivors=survivors, 
                           hunters=hunters,
                           result=prediction_result,
                           total_samples=total_samples,
                           selected=selected_bans,
                           message=message)

# 統計ページ (案①)
@app.route('/stats')
def stats():
    db = get_db()
    hunter_id = request.args.get('hunter_id')
    stats_data = []
    current_hunter = None
    
    if hunter_id:
        stats_data = get_stats_by_hunter(hunter_id)
        current_hunter = db.execute('SELECT display_name FROM m_hunters WHERE id = ?', (hunter_id,)).fetchone()

    hunters = db.execute('SELECT id, display_name FROM m_hunters ORDER BY id').fetchall()
    return render_template('stats.html', hunters=hunters, stats_data=stats_data, current_hunter=current_hunter)

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print("Warning: Run init_master.py first to create the database.")
        pass