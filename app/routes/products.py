from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app.models import db, Product

products_bp = Blueprint('product', __name__)

@products_bp.route('/product')
@login_required
def list_products():
    products = Product.query.filter_by(
        tenant_id=current_user.tenant_id,
        active=True
    ).order_by(Product.name).all()
    return render_template('product/list.html', products=products)


@products_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        product = Product(
            tenant_id   = current_user.tenant_id,
            name        = request.form.get('name'),
            price       = float(request.form.get('price')),
            category    = request.form.get('category'),
            description = request.form.get('description')
        )
        db.session.add(product)
        db.session.commit()
        flash('Đã thêm sản phẩm!', 'success')
        return redirect(url_for('product.list_products'))
    return render_template('product/form.html', product=None)


@products_bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id
    ).first()
    if not product:
        abort(404)

    if request.method == 'POST':
        product.name        = request.form.get('name')
        product.price       = float(request.form.get('price'))
        product.category    = request.form.get('category')
        product.description = request.form.get('description')
        db.session.commit()
        flash('Đã cập nhật!', 'success')
        return redirect(url_for('product.list_products'))
    return render_template('product/form.html', product=product)


@products_bp.route('/product/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.filter_by(
        id=product_id,
        tenant_id=current_user.tenant_id
    ).first()
    if not product:
        abort(404)
    product.active = False
    db.session.commit()
    flash('Đã xoá sản phẩm.', 'success')
    return redirect(url_for('product.list_products'))