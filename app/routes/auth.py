import os
import shutil
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Tenant

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_masteradmin:
            return redirect(url_for('auth.masteradmin_dashboard'))
        return redirect(url_for('transactions.pos_page'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        shop_name = request.form.get('shop_name').strip()
        email     = request.form.get('email').strip()
        password  = request.form.get('password')
        slug      = shop_name.lower().replace(' ', '_')

        if Tenant.query.filter_by(slug=slug).first():
            flash('Tên shop đã tồn tại.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng.', 'danger')
            return redirect(url_for('auth.register'))

        tenant = Tenant(name=shop_name, slug=slug)
        db.session.add(tenant)
        db.session.flush()

        user = User(tenant_id=tenant.id, email=email, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash(f'Đăng ký thành công! Mời đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            if user.is_masteradmin:
                return redirect(url_for('auth.masteradmin_dashboard'))
            return redirect(url_for('transactions.pos_page'))

        flash('Email hoặc mật khẩu không đúng.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/users')
@login_required
def list_users():
    if current_user.role != 'admin':
        flash('Không có quyền.', 'danger')
        return redirect(url_for('transactions.pos_page'))
    users = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    return render_template('auth/users.html', users=users)


@auth_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Không có quyền.', 'danger')
        return redirect(url_for('transactions.pos_page'))

    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        role     = request.form.get('role', 'staff')

        if User.query.filter_by(email=email).first():
            flash('Email đã tồn tại.', 'danger')
            return redirect(url_for('auth.add_user'))

        user = User(tenant_id=current_user.tenant_id, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'Đã thêm {email}!', 'success')
        return redirect(url_for('auth.list_users'))

    return render_template('auth/add_user.html')


@auth_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Không có quyền.', 'danger')
        return redirect(url_for('transactions.pos_page'))

    user = User.query.filter_by(
        id=user_id, tenant_id=current_user.tenant_id
    ).first_or_404()

    if user.id == current_user.id:
        flash('Không thể xoá chính mình.', 'danger')
        return redirect(url_for('auth.list_users'))

    db.session.delete(user)
    db.session.commit()
    flash('Đã xoá nhân viên.', 'success')
    return redirect(url_for('auth.list_users'))


@auth_bp.route('/tenant/delete', methods=['POST'])
@login_required
def delete_tenant():
    if current_user.role != 'admin':
        flash('Không có quyền.', 'danger')
        return redirect(url_for('transactions.pos_page'))

    tenant = current_user.tenant
    User.query.filter_by(tenant_id=tenant.id).delete()
    db.session.delete(tenant)
    db.session.commit()
    logout_user()
    flash('Đã xoá shop thành công.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin')
@login_required
def masteradmin_dashboard():
    if not current_user.is_masteradmin:
        flash('Không có quyền.', 'danger')
        return redirect(url_for('transactions.pos_page'))

    tenants     = Tenant.query.order_by(Tenant.created_at.desc()).all()
    tenant_data = []
    for t in tenants:
        user_count = User.query.filter_by(tenant_id=t.id).count()
        tenant_data.append({
            'tenant'    : t,
            'user_count': user_count,
        })

    return render_template('admin/dashboard.html', tenant_data=tenant_data)


@auth_bp.route('/admin/tenant/<int:tenant_id>/delete', methods=['POST'])
@login_required
def masteradmin_delete_tenant(tenant_id):
    if not current_user.is_masteradmin:
        flash('Không có quyền.', 'danger')
        return redirect(url_for('auth.masteradmin_dashboard'))

    tenant = Tenant.query.get_or_404(tenant_id)
    User.query.filter_by(tenant_id=tenant.id).delete()
    db.session.delete(tenant)
    db.session.commit()

    flash(f'Đã xoá tenant "{tenant.name}".', 'success')
    return redirect(url_for('auth.masteradmin_dashboard'))