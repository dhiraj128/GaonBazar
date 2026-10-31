import sqlite3
import json
from datetime import datetime, timezone

def generate_snapshot():
    conn = sqlite3.connect('backend/gaonbazar.db')
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in c.fetchall()]

    baseline = {
        'created_at': datetime.now(timezone.utc).isoformat(),
        'source': 'backend/gaonbazar.db',
        'tables': {}
    }

    for tbl in sorted(tables):
        c.execute(f'SELECT COUNT(*) FROM "{tbl}"')
        cnt = c.fetchone()[0]
        
        c.execute(f'PRAGMA table_info("{tbl}")')
        cols = [{'cid': r[0], 'name': r[1], 'type': r[2], 'notnull': r[3], 'dflt_value': r[4], 'pk': r[5]} for r in c.fetchall()]
        
        baseline['tables'][tbl] = {
            'row_count': cnt,
            'columns_count': len(cols),
            'columns': cols
        }

    c.execute('SELECT COALESCE(SUM(total_amount), 0) FROM orders')
    baseline['orders_sum_inr'] = float(c.fetchone()[0])

    c.execute('SELECT COALESCE(SUM(amount), 0) FROM payment_transactions')
    baseline['payments_sum_inr'] = float(c.fetchone()[0])

    # Check orphan metrics
    c.execute('''
        SELECT COUNT(*) FROM orders 
        WHERE user_id IS NOT NULL AND user_id != '' AND user_id NOT IN (SELECT id FROM users)
    ''')
    baseline['orphan_orders_missing_users'] = c.fetchone()[0]

    c.execute('''
        SELECT COUNT(*) FROM order_items 
        WHERE order_id NOT IN (SELECT id FROM orders)
    ''')
    baseline['orphan_order_items_missing_orders'] = c.fetchone()[0]

    c.execute('''
        SELECT COUNT(*) FROM payment_transactions 
        WHERE order_id NOT IN (SELECT id FROM orders)
    ''')
    baseline['orphan_payments_missing_orders'] = c.fetchone()[0]

    with open('docs/audits/PHASE3A_BASELINE_AUDIT_SNAPSHOT.json', 'w') as f:
        json.dump(baseline, f, indent=2)

    print('Baseline audit snapshot written successfully!')
    print(f'Total tables: {len(tables)}')
    print(f'Orders: {baseline["tables"]["orders"]["row_count"]} (Rs.{baseline["orders_sum_inr"]:.2f})')
    print(f'Payments: {baseline["tables"]["payment_transactions"]["row_count"]} (Rs.{baseline["payments_sum_inr"]:.2f})')
    print(f'Orphan orders (missing user): {baseline["orphan_orders_missing_users"]}')
    print(f'Orphan items (missing order): {baseline["orphan_order_items_missing_orders"]}')
    print(f'Orphan payments (missing order): {baseline["orphan_payments_missing_orders"]}')

if __name__ == '__main__':
    generate_snapshot()
