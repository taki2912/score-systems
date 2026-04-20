import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_migrate import Migrate
from datetime import datetime
from models import db, User, Club, Member, ScoreChange, ViewRequest
from auth import (hash_password, verify_password, login_user, logout_user,
                  get_current_user, login_required, admin_required, super_admin_required)
import config

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
migrate = Migrate(app, db)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_avatar(file):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None


def format_score(value):
    if value is None:
        return '0'
    if value == int(value):
        return f'{int(value):,}'
    return f'{value:,.1f}'


app.jinja_env.filters['score_fmt'] = format_score


@app.context_processor
def inject_clubs():
    return dict(clubs_nav=Club.query.all())


def init_db():
    with app.app_context():
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        db.create_all()
        if User.query.filter_by(username='admin').first() is None:
            admin = User(
                username='admin',
                password_hash=hash_password('admin123'),
                role='super_admin',
                must_change_password=True
            )
            db.session.add(admin)
            db.session.commit()
            print('超级管理员已创建: admin / admin123 (首次登录请修改密码)')
        # migrate: set existing admin to super_admin
        existing = User.query.filter_by(username='admin', role='admin').first()
        if existing:
            existing.role = 'super_admin'
            db.session.commit()
        if Club.query.filter_by(name='86硬上山').first() is None:
            club = Club(name='86硬上山', description='86硬上山俱乐部')
            db.session.add(club)
            db.session.commit()
            print('默认俱乐部已创建: 86硬上山')


# ── 首页: 俱乐部列表(游客可访问) ──────────────────────────

@app.route('/')
def index():
    clubs = Club.query.order_by(Club.created_at.desc()).all()
    current_user = get_current_user()
    total_members = sum(c.members.filter_by(is_active=True).count() for c in clubs)
    return render_template('index.html', clubs=clubs, current_user=current_user,
                           total_members=total_members)


# ── 俱乐部详情: 成员列表(游客可访问) ─────────────────────

@app.route('/club/<int:club_id>')
def club_detail(club_id):
    club = Club.query.get_or_404(club_id)
    members = Member.query.filter_by(club_id=club_id, is_active=True)\
        .order_by(Member.score.desc()).all()
    current_user = get_current_user()
    return render_template('club_detail.html', club=club, members=members,
                           current_user=current_user)


# ── 成员详情(游客可点击进入, 但历史需申请) ────────────────

@app.route('/member/<int:member_id>')
def member_detail(member_id):
    member = Member.query.get_or_404(member_id)
    current_user = get_current_user()
    can_view_history = False
    existing_request = None

    if current_user and current_user.is_admin:
        can_view_history = True
    elif current_user:
        existing_request = ViewRequest.query.filter_by(
            member_id=member_id, applicant_id=current_user.id
        ).first()
        if existing_request and existing_request.status == 'approved':
            can_view_history = True

    changes = []
    if can_view_history:
        changes = ScoreChange.query.filter_by(member_id=member_id)\
            .order_by(ScoreChange.created_at.desc()).all()

    return render_template('member_detail.html', member=member, changes=changes,
                           current_user=current_user, can_view_history=can_view_history,
                           existing_request=existing_request)


# ── 申请查看历史(确认本人) ─────────────────────────────────

@app.route('/member/<int:member_id>/request_view', methods=['GET', 'POST'])
def request_view(member_id):
    member = Member.query.get_or_404(member_id)
    current_user = get_current_user()

    if request.method == 'POST':
        is_self = request.form.get('is_self') == 'yes'
        not_self_reason = request.form.get('not_self_reason', '').strip()

        if not is_self and not not_self_reason:
            flash('非本人查看需填写原因说明', 'danger')
            return redirect(url_for('request_view', member_id=member_id))

        existing = ViewRequest.query.filter_by(
            member_id=member_id, applicant_id=current_user.id
        ).first() if current_user else None

        if existing:
            flash('您已提交过申请，请等待审核', 'warning')
            return redirect(url_for('member_detail', member_id=member_id))

        vr = ViewRequest(
            member_id=member_id,
            applicant_id=current_user.id,
            is_self_confirmed=is_self,
            not_self_reason=not_self_reason if not is_self else None,
            status='pending'
        )
        db.session.add(vr)
        db.session.commit()
        flash('申请已提交，等待管理员审核', 'success')
        return redirect(url_for('member_detail', member_id=member_id))

    return render_template('request_view.html', member=member, current_user=current_user)


# ── 登录/登出/注册 ─────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user is None or not verify_password(user.password_hash, password):
            flash('用户名或密码错误', 'danger')
            return render_template('login.html')

        if not user.is_active:
            flash('该账号已被禁用', 'danger')
            return render_template('login.html')

        login_user(user)

        if user.must_change_password:
            flash('请修改默认密码', 'warning')
            return redirect(url_for('change_password'))

        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_pwd = request.form.get('confirm_password', '')

        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return render_template('register.html')

        if len(username) < 2 or len(username) > 20:
            flash('用户名长度2-20位', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('密码至少6位', 'danger')
            return render_template('register.html')

        if password != confirm_pwd:
            flash('两次密码不一致', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return render_template('register.html')

        user = User(
            username=username,
            password_hash=hash_password(password),
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('注册成功，欢迎！', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('index'))


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_pwd = request.form.get('old_password', '')
        new_pwd = request.form.get('new_password', '')
        confirm_pwd = request.form.get('confirm_password', '')

        user = get_current_user()
        if not verify_password(user.password_hash, old_pwd):
            flash('原密码错误', 'danger')
            return redirect(url_for('change_password'))

        if len(new_pwd) < 6:
            flash('新密码至少6位', 'danger')
            return redirect(url_for('change_password'))

        if new_pwd != confirm_pwd:
            flash('两次密码不一致', 'danger')
            return redirect(url_for('change_password'))

        user.password_hash = hash_password(new_pwd)
        user.must_change_password = False
        db.session.commit()
        flash('密码修改成功', 'success')
        return redirect(url_for('index'))

    return render_template('change_password.html',
                           must_change=get_current_user().must_change_password)


# ── 超级管理员: 俱乐部管理 ────────────────────────────────

@app.route('/admin/clubs')
@super_admin_required
def admin_clubs():
    clubs = Club.query.order_by(Club.created_at.desc()).all()
    return render_template('admin/clubs.html', clubs=clubs)


@app.route('/admin/club/create', methods=['GET', 'POST'])
@super_admin_required
def admin_create_club():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('俱乐部名称不能为空', 'danger')
            return redirect(url_for('admin_create_club'))

        if Club.query.filter_by(name=name).first():
            flash('俱乐部名称已存在', 'danger')
            return redirect(url_for('admin_create_club'))

        club = Club(name=name, description=description)
        db.session.add(club)
        db.session.commit()
        flash(f'俱乐部 {name} 创建成功', 'success')
        return redirect(url_for('admin_clubs'))

    return render_template('admin/create_club.html')


@app.route('/admin/club/<int:club_id>/delete', methods=['POST'])
@super_admin_required
def admin_delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    name = club.name
    db.session.delete(club)
    db.session.commit()
    flash(f'俱乐部 {name} 已删除', 'success')
    return redirect(url_for('admin_clubs'))


# ── 管理员: 成员管理(admin可查看+编辑分数, 超级管理员可增删) ──

@app.route('/admin/club/<int:club_id>/members')
@admin_required
def admin_club_members(club_id):
    club = Club.query.get_or_404(club_id)
    members = Member.query.filter_by(club_id=club_id).order_by(Member.score.desc()).all()
    current_user = get_current_user()
    return render_template('admin/club_members.html', club=club, members=members,
                           current_user=current_user)


@app.route('/admin/club/<int:club_id>/member/create', methods=['GET', 'POST'])
@admin_required
def admin_create_member(club_id):
    club = Club.query.get_or_404(club_id)

    if request.method == 'POST':
        display_id = request.form.get('display_id', '').strip()
        name = request.form.get('name', '').strip()
        score = request.form.get('score', type=float, default=0.0)
        avatar_file = request.files.get('avatar')

        if not display_id or not name:
            flash('ID和名称不能为空', 'danger')
            return redirect(url_for('admin_create_member', club_id=club_id))

        if Member.query.filter_by(club_id=club_id, display_id=display_id).first():
            flash('该俱乐部下ID已存在', 'danger')
            return redirect(url_for('admin_create_member', club_id=club_id))

        avatar_name = save_avatar(avatar_file)

        member = Member(
            club_id=club_id,
            display_id=display_id,
            name=name,
            score=score,
            avatar=avatar_name
        )
        db.session.add(member)
        db.session.commit()
        flash(f'成员 {name} 创建成功', 'success')
        return redirect(url_for('admin_club_members', club_id=club_id))

    return render_template('admin/create_member.html', club=club)


@app.route('/admin/member/<int:member_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_member(member_id):
    member = Member.query.get_or_404(member_id)

    if request.method == 'POST':
        current_user = get_current_user()

        if current_user.is_super_admin:
            name = request.form.get('name', '').strip()
            display_id = request.form.get('display_id', '').strip()
            if name:
                member.name = name
            if display_id:
                member.display_id = display_id

            avatar_file = request.files.get('avatar')
            if avatar_file and allowed_file(avatar_file.filename):
                if member.avatar:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], member.avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                member.avatar = save_avatar(avatar_file)

        new_score = request.form.get('new_score', type=float)
        reason = request.form.get('reason', '').strip()

        if new_score is not None and new_score != member.score:
            if not reason:
                flash('修改分数必须填写原因', 'danger')
                return redirect(url_for('admin_edit_member', member_id=member_id))

            change = ScoreChange(
                member_id=member.id,
                old_score=member.score,
                new_score=new_score,
                change_type='admin_edit',
                reason=reason,
                is_self_confirmed=True,
                status='approved',
                applicant_id=current_user.id,
                reviewed_by=current_user.id,
                reviewed_at=datetime.now()
            )
            member.score = new_score
            db.session.add(change)

        db.session.commit()
        flash(f'{member.name} 信息已更新', 'success')
        return redirect(url_for('admin_club_members', club_id=member.club_id))

    current_user = get_current_user()
    return render_template('admin/edit_member.html', member=member, current_user=current_user)


@app.route('/admin/member/<int:member_id>/toggle_active', methods=['POST'])
@super_admin_required
def admin_toggle_member(member_id):
    member = Member.query.get_or_404(member_id)
    member.is_active = not member.is_active
    db.session.commit()
    status = '启用' if member.is_active else '禁用'
    flash(f'{member.name} 已{status}', 'success')
    return redirect(url_for('admin_club_members', club_id=member.club_id))


@app.route('/admin/member/<int:member_id>/delete', methods=['POST'])
@super_admin_required
def admin_delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    club_id = member.club_id
    if member.avatar:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], member.avatar)
        if os.path.exists(old_path):
            os.remove(old_path)
    db.session.delete(member)
    db.session.commit()
    flash('成员已删除', 'success')
    return redirect(url_for('admin_club_members', club_id=club_id))


# ── 超级管理员: 用户账号管理 + 权限管理 ────────────────────

@app.route('/admin/users')
@super_admin_required
def admin_users():
    users = User.query.order_by(User.id).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/user/create', methods=['GET', 'POST'])
@super_admin_required
def admin_create_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')

        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return redirect(url_for('admin_create_user'))

        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('admin_create_user'))

        if len(password) < 6:
            flash('密码至少6位', 'danger')
            return redirect(url_for('admin_create_user'))

        user = User(
            username=username,
            password_hash=hash_password(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        flash(f'用户 {username} 创建成功', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin/create_user.html')


@app.route('/admin/user/<int:user_id>/toggle_active', methods=['POST'])
@super_admin_required
def admin_toggle_user(user_id):
    target = User.query.get_or_404(user_id)
    if target.is_super_admin:
        flash('不能禁用超级管理员', 'danger')
        return redirect(url_for('admin_users'))
    target.is_active = not target.is_active
    db.session.commit()
    status = '启用' if target.is_active else '禁用'
    flash(f'用户 {target.username} 已{status}', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/reset_password', methods=['POST'])
@super_admin_required
def admin_reset_password(user_id):
    target = User.query.get_or_404(user_id)
    new_pwd = request.form.get('new_password', '')
    if len(new_pwd) < 6:
        flash('密码至少6位', 'danger')
        return redirect(url_for('admin_users'))
    target.password_hash = hash_password(new_pwd)
    target.must_change_password = True
    db.session.commit()
    flash(f'{target.username} 密码已重置', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/user/<int:user_id>/change_role', methods=['POST'])
@super_admin_required
def admin_change_role(user_id):
    target = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if new_role not in ('user', 'admin', 'super_admin'):
        flash('无效角色', 'danger')
        return redirect(url_for('admin_users'))

    if target.is_super_admin and target.username == 'admin' and new_role != 'super_admin':
        flash('不能修改默认超级管理员权限', 'danger')
        return redirect(url_for('admin_users'))

    old_role = target.role_display
    target.role = new_role
    # update session if changing own role
    if target.id == session.get('user_id'):
        session['role'] = new_role
    db.session.commit()
    flash(f'{target.username} 角色已从 {old_role} 变更为 {target.role_display}', 'success')
    return redirect(url_for('admin_users'))


# ── 管理员: 审核查看申请 ──────────────────────────────────

@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    status_filter = request.args.get('status', 'pending')
    if status_filter == 'all':
        requests_list = ViewRequest.query.order_by(ViewRequest.created_at.desc()).all()
    else:
        requests_list = ViewRequest.query.filter_by(status=status_filter)\
            .order_by(ViewRequest.created_at.desc()).all()
    return render_template('admin/review_list.html', requests_list=requests_list,
                           current_filter=status_filter)


@app.route('/admin/review/<int:request_id>', methods=['GET', 'POST'])
@admin_required
def admin_review_request(request_id):
    vr = ViewRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        action = request.form.get('action')
        if action not in ('approve', 'reject'):
            flash('无效操作', 'danger')
            return redirect(url_for('admin_reviews'))

        vr.status = 'approved' if action == 'approve' else 'rejected'
        vr.reviewed_by = get_current_user().id
        vr.reviewed_at = datetime.now()

        if action == 'approve':
            flash('申请已通过', 'success')
        else:
            flash('申请已驳回', 'info')

        db.session.commit()
        return redirect(url_for('admin_reviews'))

    return render_template('admin/review_detail.html', vr=vr)


# ── 管理员: 分数变动记录 ──────────────────────────────────

@app.route('/admin/score_changes')
@admin_required
def admin_score_changes():
    changes = ScoreChange.query.order_by(ScoreChange.created_at.desc()).all()
    return render_template('admin/score_changes.html', changes=changes)


# ── 成员历史数据 API (图表用) ──────────────────────────────

@app.route('/api/member/<int:member_id>/chart_data')
def member_chart_data(member_id):
    current_user = get_current_user()
    can_view = False
    if current_user and current_user.is_admin:
        can_view = True
    elif current_user:
        vr = ViewRequest.query.filter_by(
            member_id=member_id, applicant_id=current_user.id, status='approved'
        ).first()
        if vr:
            can_view = True

    if not can_view:
        return jsonify({'error': 'no permission'}), 403

    changes = ScoreChange.query.filter_by(member_id=member_id, status='approved')\
        .order_by(ScoreChange.created_at.asc()).all()

    labels = []
    scores = []
    for c in changes:
        labels.append(c.created_at.strftime('%m/%d'))
        scores.append(c.new_score)

    return jsonify({'labels': labels, 'scores': scores})


# ── 启动 ──────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
