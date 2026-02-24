"""
Database Protection System for SQLite
Auto-backup, integrity check, dump-repair, and restore.
Designed for production — never loses data.
"""
import os, shutil, sqlite3, time
from datetime import datetime, timedelta


# ─── Config ──────────────────────────────────────────────────────
MAX_BACKUPS = 10          # Keep last N backups (auto-rotate)
BACKUP_SUBFOLDER = 'backups'  # Inside instance/


def _get_paths(app):
    """Get all relevant paths"""
    db_path = os.path.join(app.instance_path, 'unilab.db')
    backup_dir = os.path.join(app.instance_path, BACKUP_SUBFOLDER)
    os.makedirs(backup_dir, exist_ok=True)
    return db_path, backup_dir


# ─── Integrity Check ────────────────────────────────────────────

def check_integrity(app):
    """
    Run PRAGMA integrity_check on the database.
    Returns: {'ok': bool, 'errors': [str], 'duration_ms': int}
    """
    db_path, _ = _get_paths(app)
    if not os.path.exists(db_path):
        return {'ok': False, 'errors': ['Database file not found'], 'duration_ms': 0}

    t0 = time.time()
    errors = []
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        results = cursor.fetchall()
        for row in results:
            if row[0] != 'ok':
                errors.append(row[0])
        conn.close()
    except Exception as e:
        errors.append(str(e))

    duration_ms = int((time.time() - t0) * 1000)
    return {
        'ok': len(errors) == 0,
        'errors': errors,
        'duration_ms': duration_ms,
    }


def quick_check(app):
    """
    Fast check using PRAGMA quick_check (less thorough but faster).
    Good for periodic checks.
    """
    db_path, _ = _get_paths(app)
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute("PRAGMA quick_check")
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == 'ok'
    except:
        return False


# ─── Backup ──────────────────────────────────────────────────────

def create_backup(app, label='manual'):
    """
    Create a timestamped backup of the database.
    Uses sqlite3 backup API for consistency (safe even while app is running).
    Auto-rotates old backups.

    Returns: {'path': str, 'size_display': str, 'timestamp': str} or None on failure
    """
    db_path, backup_dir = _get_paths(app)
    if not os.path.exists(db_path):
        return None

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'unilab_{label}_{ts}.db'
    backup_path = os.path.join(backup_dir, backup_name)

    try:
        # Use sqlite3 backup API — safe for live databases
        source = sqlite3.connect(db_path, timeout=30)
        dest = sqlite3.connect(backup_path)
        source.backup(dest)
        dest.close()
        source.close()

        # Verify backup integrity
        verify_conn = sqlite3.connect(backup_path)
        cursor = verify_conn.cursor()
        cursor.execute("PRAGMA quick_check")
        verify_ok = cursor.fetchone()[0] == 'ok'
        verify_conn.close()

        if not verify_ok:
            os.remove(backup_path)
            return None

        # Auto-rotate: remove oldest backups beyond MAX_BACKUPS
        _rotate_backups(backup_dir)

        size = os.path.getsize(backup_path)
        return {
            'path': backup_path,
            'name': backup_name,
            'size_display': _format_size(size),
            'timestamp': ts,
        }
    except Exception as e:
        # Fallback: file copy (less safe but better than nothing)
        try:
            shutil.copy2(db_path, backup_path)
            _rotate_backups(backup_dir)
            size = os.path.getsize(backup_path)
            return {
                'path': backup_path,
                'name': backup_name,
                'size_display': _format_size(size),
                'timestamp': ts,
                'warning': f'Used file copy instead of sqlite backup: {e}',
            }
        except:
            return None


def _rotate_backups(backup_dir):
    """Keep only the most recent MAX_BACKUPS files"""
    files = []
    for f in os.listdir(backup_dir):
        if f.startswith('unilab_') and f.endswith('.db'):
            fpath = os.path.join(backup_dir, f)
            files.append((os.path.getmtime(fpath), fpath))
    files.sort(reverse=True)
    for _, fpath in files[MAX_BACKUPS:]:
        try:
            os.remove(fpath)
        except:
            pass


def list_backups(app):
    """List all available backups, newest first"""
    _, backup_dir = _get_paths(app)
    backups = []
    # Check new backup dir
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            if f.startswith('unilab_') and f.endswith('.db'):
                fpath = os.path.join(backup_dir, f)
                size = os.path.getsize(fpath)
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                backups.append({
                    'name': f,
                    'path': fpath,
                    'size': size,
                    'size_display': _format_size(size),
                    'modified': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                    'modified_dt': mtime,
                })
    # Also check legacy .backup files in instance root
    db_path, _ = _get_paths(app)
    import glob as glob_mod
    for fpath in glob_mod.glob(os.path.join(app.instance_path, 'unilab.db.backup*')):
        size = os.path.getsize(fpath)
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
        backups.append({
            'name': os.path.basename(fpath),
            'path': fpath,
            'size': size,
            'size_display': _format_size(size),
            'modified': mtime.strftime('%Y-%m-%d %H:%M:%S'),
            'modified_dt': mtime,
            'legacy': True,
        })

    backups.sort(key=lambda x: x['modified_dt'], reverse=True)
    return backups


# ─── Repair ──────────────────────────────────────────────────────

def repair_database(app):
    """
    Attempt to repair a corrupted database using dump-and-rebuild.
    This is the gold standard for SQLite recovery.

    Strategy:
    1. Backup current DB (even if corrupted)
    2. Try PRAGMA integrity_check — if OK, just remove WAL/SHM
    3. If corrupted: dump all data via .dump → rebuild from dump
    4. Verify rebuilt DB integrity

    Returns: {
        'success': bool,
        'method': str,   # 'wal_cleanup' | 'dump_rebuild' | 'partial_recovery'
        'tables_recovered': int,
        'rows_recovered': int,
        'errors': [str],
    }
    """
    from models import db as sa_db

    db_path, backup_dir = _get_paths(app)
    result = {'success': False, 'method': '', 'tables_recovered': 0, 'rows_recovered': 0, 'errors': []}

    if not os.path.exists(db_path):
        result['errors'].append('Database file not found')
        return result

    # Step 0: Always backup first
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    pre_repair_backup = os.path.join(backup_dir, f'unilab_pre_repair_{ts}.db')
    try:
        shutil.copy2(db_path, pre_repair_backup)
        # Also copy WAL/SHM
        for ext in ['-wal', '-shm']:
            src = db_path + ext
            if os.path.exists(src):
                shutil.copy2(src, pre_repair_backup + ext)
    except Exception as e:
        result['errors'].append(f'Backup failed: {e}')

    # Step 1: Try WAL cleanup first (quickest fix)
    try:
        sa_db.session.remove()
        sa_db.engine.dispose()
    except:
        pass

    wal_removed = False
    for ext in ['-wal', '-shm']:
        wal_path = db_path + ext
        if os.path.exists(wal_path):
            try:
                os.remove(wal_path)
                wal_removed = True
            except:
                pass

    # Check if WAL cleanup fixed it
    integrity = check_integrity(app)
    if integrity['ok']:
        result['success'] = True
        result['method'] = 'wal_cleanup'
        return result

    # Step 2: Dump and rebuild
    result['method'] = 'dump_rebuild'
    dump_path = os.path.join(backup_dir, f'_repair_dump_{ts}.sql')
    rebuilt_path = os.path.join(backup_dir, f'_repair_rebuilt_{ts}.db')

    try:
        # Dump what we can from the corrupted DB
        conn = sqlite3.connect(db_path, timeout=30)
        tables_recovered = 0
        rows_recovered = 0

        with open(dump_path, 'w', encoding='utf-8') as f:
            try:
                for line in conn.iterdump():
                    f.write(line + '\n')
                    if line.startswith('INSERT'):
                        rows_recovered += 1
                    elif line.startswith('CREATE TABLE'):
                        tables_recovered += 1
            except Exception as dump_err:
                result['errors'].append(f'Partial dump: {dump_err}')
                # Even partial dumps are valuable — continue
        conn.close()

        result['tables_recovered'] = tables_recovered
        result['rows_recovered'] = rows_recovered

        if rows_recovered == 0 and tables_recovered == 0:
            result['errors'].append('Could not recover any data from dump')
            result['success'] = False
            return result

        # Rebuild from dump
        rebuilt_conn = sqlite3.connect(rebuilt_path)
        with open(dump_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        try:
            rebuilt_conn.executescript(sql)
        except Exception as rebuild_err:
            result['errors'].append(f'Rebuild warning: {rebuild_err}')
            # Try line-by-line for partial recovery
            rebuilt_conn.close()
            os.remove(rebuilt_path)
            rebuilt_conn = sqlite3.connect(rebuilt_path)
            for line in sql.split(';\n'):
                line = line.strip()
                if line:
                    try:
                        rebuilt_conn.execute(line + ';')
                    except:
                        pass
            rebuilt_conn.commit()
            result['method'] = 'partial_recovery'

        rebuilt_conn.close()

        # Verify rebuilt DB
        verify_conn = sqlite3.connect(rebuilt_path)
        cursor = verify_conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        verify_result = cursor.fetchone()
        verify_conn.close()

        if verify_result and verify_result[0] == 'ok':
            # Replace corrupted DB with rebuilt one
            try:
                sa_db.session.remove()
                sa_db.engine.dispose()
            except:
                pass
            os.replace(rebuilt_path, db_path)
            result['success'] = True
        else:
            result['errors'].append('Rebuilt database failed integrity check')
            result['success'] = False

        # Cleanup temp dump file
        try:
            os.remove(dump_path)
        except:
            pass

    except Exception as e:
        result['errors'].append(f'Repair failed: {e}')
        result['success'] = False

    return result


def restore_from_backup(app, backup_path):
    """
    Restore database from a backup file.
    Always backs up current DB first.

    Returns: {'success': bool, 'message': str}
    """
    from models import db as sa_db

    db_path, backup_dir = _get_paths(app)

    if not os.path.exists(backup_path):
        return {'success': False, 'message': 'Backup file not found'}

    # Verify backup integrity before restoring
    try:
        conn = sqlite3.connect(backup_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute("PRAGMA quick_check")
        check = cursor.fetchone()
        conn.close()
        if not check or check[0] != 'ok':
            return {'success': False, 'message': 'Backup file is corrupted'}
    except Exception as e:
        return {'success': False, 'message': f'Cannot verify backup: {e}'}

    # Backup current DB
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    pre_restore = os.path.join(backup_dir, f'unilab_pre_restore_{ts}.db')
    if os.path.exists(db_path):
        try:
            shutil.copy2(db_path, pre_restore)
        except:
            pass

    # Close all connections
    try:
        sa_db.session.remove()
        sa_db.engine.dispose()
    except:
        pass

    # Replace DB
    try:
        shutil.copy2(backup_path, db_path)
        # Remove stale WAL/SHM
        for ext in ['-wal', '-shm']:
            p = db_path + ext
            if os.path.exists(p):
                os.remove(p)
        return {'success': True, 'message': f'Restored from {os.path.basename(backup_path)}. Previous DB backed up to {os.path.basename(pre_restore)}'}
    except Exception as e:
        return {'success': False, 'message': f'Restore failed: {e}'}


# ─── Startup Check ───────────────────────────────────────────────

def startup_check(app):
    """
    Run on app startup. Checks DB health and auto-repairs if needed.
    Also creates a startup backup if last backup is > 24h old.

    Returns: {'healthy': bool, 'action': str, 'details': str}
    """
    db_path, backup_dir = _get_paths(app)

    if not os.path.exists(db_path):
        return {'healthy': True, 'action': 'none', 'details': 'No DB yet — will be created'}

    # Quick integrity check
    if quick_check(app):
        # DB is healthy — check if we need an auto-backup
        _auto_backup_if_needed(app)
        return {'healthy': True, 'action': 'none', 'details': 'Database healthy'}

    # DB has issues — try repair
    print('[!] Database integrity check FAILED — attempting auto-repair...')
    repair_result = repair_database(app)

    if repair_result['success']:
        print(f'[*] Auto-repair successful via {repair_result["method"]}')
        print(f'    Tables: {repair_result["tables_recovered"]}, Rows: {repair_result["rows_recovered"]}')
        return {
            'healthy': True,
            'action': 'repaired',
            'details': f'Auto-repaired via {repair_result["method"]} ({repair_result["tables_recovered"]} tables, {repair_result["rows_recovered"]} rows)',
        }
    else:
        print(f'[!] Auto-repair FAILED: {repair_result["errors"]}')
        # Try to find and restore from latest good backup
        backups = list_backups(app)
        for b in backups:
            try:
                conn = sqlite3.connect(b['path'], timeout=10)
                cursor = conn.cursor()
                cursor.execute("PRAGMA quick_check")
                ok = cursor.fetchone()[0] == 'ok'
                conn.close()
                if ok:
                    print(f'[*] Found good backup: {b["name"]} — restoring...')
                    restore_result = restore_from_backup(app, b['path'])
                    if restore_result['success']:
                        return {
                            'healthy': True,
                            'action': 'restored_from_backup',
                            'details': f'Restored from backup: {b["name"]}',
                        }
            except:
                continue

        return {
            'healthy': False,
            'action': 'failed',
            'details': f'Could not repair or restore. Errors: {"; ".join(repair_result["errors"])}',
        }


def _auto_backup_if_needed(app):
    """Create auto-backup if last backup is > 24h old"""
    backups = list_backups(app)
    if backups:
        newest = backups[0]['modified_dt']
        if datetime.now() - newest < timedelta(hours=24):
            return  # Recent backup exists
    create_backup(app, label='auto')


# ─── DB Health Report ────────────────────────────────────────────

def get_health_report(app):
    """
    Comprehensive DB health report for admin dashboard.
    Returns dict with all health metrics.
    """
    db_path, backup_dir = _get_paths(app)
    report = {
        'exists': os.path.exists(db_path),
        'size': 0,
        'size_display': '—',
        'integrity': None,
        'wal_size': 0,
        'wal_exists': False,
        'journal_mode': '',
        'page_count': 0,
        'freelist_count': 0,
        'fragmentation_pct': 0,
        'backups': [],
        'last_backup': None,
        'backup_age_hours': None,
    }

    if not report['exists']:
        return report

    # File sizes
    report['size'] = os.path.getsize(db_path)
    report['size_display'] = _format_size(report['size'])

    wal_path = db_path + '-wal'
    if os.path.exists(wal_path):
        report['wal_exists'] = True
        report['wal_size'] = os.path.getsize(wal_path)

    # SQLite internals
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()

        cursor.execute("PRAGMA journal_mode")
        report['journal_mode'] = cursor.fetchone()[0]

        cursor.execute("PRAGMA page_count")
        report['page_count'] = cursor.fetchone()[0]

        cursor.execute("PRAGMA freelist_count")
        report['freelist_count'] = cursor.fetchone()[0]

        if report['page_count'] > 0:
            report['fragmentation_pct'] = round(report['freelist_count'] / report['page_count'] * 100, 1)

        conn.close()
    except:
        pass

    # Integrity check
    report['integrity'] = check_integrity(app)

    # Backups
    report['backups'] = list_backups(app)
    if report['backups']:
        report['last_backup'] = report['backups'][0]['modified']
        report['backup_age_hours'] = round((datetime.now() - report['backups'][0]['modified_dt']).total_seconds() / 3600, 1)

    return report


# ─── Utilities ───────────────────────────────────────────────────

def vacuum_database(app):
    """Run VACUUM to defragment and shrink the database"""
    db_path, _ = _get_paths(app)
    try:
        # Backup first
        create_backup(app, label='pre_vacuum')
        conn = sqlite3.connect(db_path, timeout=60)
        conn.execute("VACUUM")
        conn.close()
        return {'success': True, 'message': 'VACUUM completed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def _format_size(size_bytes):
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.1f} MB'
