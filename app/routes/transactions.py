from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Product, Transaction, TransactionItem

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/pos')
@login_required
def pos_page():
    products = Product.query.filter_by(
        tenant_id=current_user.tenant_id,
        active=True
    ).order_by(Product.category, Product.name).all()
    tax_rate = current_user.tenant.tax_rate
    return render_template('pos/pos.html', products=products, tax_rate=tax_rate)


@transactions_bp.route('/pos/checkout', methods=['POST'])
@login_required
def checkout():
    data           = request.get_json()
    items          = data.get('items', [])
    customer_email = data.get('customer_email', '').strip()

    if not items:
        return jsonify({'success': False, 'message': 'Giỏ hàng trống!'}), 400

    tax_rate  = current_user.tenant.tax_rate
    subtotal  = 0
    item_list = []

    for item in items:
        product = Product.query.filter_by(
            id=item['id'],
            tenant_id=current_user.tenant_id   # chỉ lấy product của tenant mình
        ).first()
        if not product:
            continue
        qty      = int(item['qty'])
        line_sub = product.price * qty
        subtotal += line_sub
        item_list.append({
            'name'      : product.name,
            'qty'       : qty,
            'unit_price': product.price,
            'subtotal'  : line_sub
        })

    tax_amount = round(subtotal * tax_rate, 0)
    total      = subtotal + tax_amount

    transaction = Transaction(
        tenant_id      = current_user.tenant_id,
        user_id        = current_user.id,
        tax_rate       = tax_rate,
        subtotal       = subtotal,
        tax_amount     = tax_amount,
        total          = total,
        customer_email = customer_email
    )
    db.session.add(transaction)
    db.session.flush()

    for item in item_list:
        db.session.add(TransactionItem(
            transaction_id = transaction.id,
            product_name   = item['name'],
            unit_price     = item['unit_price'],
            quantity       = item['qty'],
            subtotal       = item['subtotal']
        ))

    db.session.commit()
    # Lưu receipt lên S3
    try:
        save_receipt_to_s3(
            transaction_id = transaction.id,
            tenant_name    = current_user.tenant.name,
            item_list      = item_list,
            total          = total
        )
    except Exception as e:
        print(f'[S3 ERROR] {e}')

    email_sent = False
    if customer_email:
        try:
            send_receipt_email(
                transaction_id = transaction.id,
                item_list      = item_list,
                subtotal       = subtotal,
                tax_amount     = tax_amount,
                tax_rate       = tax_rate,
                total          = total,
                to_email       = customer_email,
                tenant_name    = current_user.tenant.name
            )
            email_sent = True
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

    return jsonify({
        'success'       : True,
        'transaction_id': transaction.id,
        'subtotal'      : subtotal,
        'tax_amount'    : tax_amount,
        'total'         : total,
        'email_sent'    : email_sent,
        'message'       : 'Thanh toán thành công!'
    })


@transactions_bp.route('/transactions')
@login_required
def list_transactions():
    transactions = Transaction.query.filter_by(
        tenant_id=current_user.tenant_id
    ).order_by(Transaction.created_at.desc()).all()
    return render_template('pos/history.html', transactions=transactions)


@transactions_bp.route('/transactions/<int:transaction_id>')
@login_required
def transaction_detail(transaction_id):
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        tenant_id=current_user.tenant_id   # không xem được transaction của tenant khác
    ).first()
    if not transaction:
        flash('Không tìm thấy giao dịch.', 'danger')
        return redirect(url_for('transactions.list_transactions'))
    return render_template('pos/receipt.html',
        transaction = transaction,
        tenant      = current_user.tenant
    )


def send_receipt_email(transaction_id, item_list, subtotal,
                       tax_amount, tax_rate, total, to_email, tenant_name):
    from app import mail
    from flask_mail import Message
    from flask import current_app

    items_html = ''
    for item in item_list:
        items_html += f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee">{item['name']}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;text-align:center">{item['qty']}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;text-align:right">{'{:,.0f}'.format(item['unit_price'])}đ</td>
          <td style="padding:8px;border-bottom:1px solid #eee;text-align:right">{'{:,.0f}'.format(item['subtotal'])}đ</td>
        </tr>"""

    tax_pct = int(tax_rate * 100)
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px">
      <h2 style="color:#212529;margin-bottom:4px">{tenant_name}</h2>
      <p style="color:#6c757d">Hoá đơn #{transaction_id}</p>
      <hr style="border:none;border-top:1px solid #dee2e6">
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-bottom:16px">
        <thead>
          <tr style="background:#212529;color:#fff">
            <th style="padding:10px;text-align:left">Sản phẩm</th>
            <th style="padding:10px;text-align:center">SL</th>
            <th style="padding:10px;text-align:right">Đơn giá</th>
            <th style="padding:10px;text-align:right">Thành tiền</th>
          </tr>
        </thead>
        <tbody>{items_html}</tbody>
      </table>
      <table width="100%" cellpadding="4">
        <tr><td style="color:#6c757d">Tạm tính</td>
            <td style="text-align:right">{'{:,.0f}'.format(subtotal)}đ</td></tr>
        <tr><td style="color:#6c757d">Thuế ({tax_pct}%)</td>
            <td style="text-align:right">{'{:,.0f}'.format(tax_amount)}đ</td></tr>
        <tr style="font-size:18px;font-weight:bold;color:#0d6efd">
          <td style="padding-top:8px">Tổng cộng</td>
          <td style="text-align:right;padding-top:8px">{'{:,.0f}'.format(total)}đ</td>
        </tr>
      </table>
      <p style="color:#6c757d;font-size:12px;text-align:center;margin-top:16px">
        Cảm ơn bạn đã mua hàng tại {tenant_name}!
      </p>
    </div>"""

    sender = current_app.config['MAIL_USERNAME']
    msg = Message(
        subject    = f'Hoá đơn #{transaction_id} — {tenant_name}',
        recipients = [to_email],
        html       = html_body,
        sender     = sender
    )
    mail.send(msg)
    print(f'[EMAIL] Sent to {to_email} via AWS SES ✓')

def save_receipt_to_s3(transaction_id, tenant_name, item_list, total):
    import boto3, json
    from flask import current_app

    s3 = boto3.client('s3', region_name=current_app.config['AWS_REGION'])

    receipt_data = {
        'transaction_id': transaction_id,
        'tenant'        : tenant_name,
        'items'         : item_list,
        'total'         : total,
    }

    s3.put_object(
        Bucket      = current_app.config['S3_BUCKET'],
        Key         = f'receipts/{tenant_name}/{transaction_id}.json',
        Body        = json.dumps(receipt_data, ensure_ascii=False),
        ContentType = 'application/json'
    )
    print(f'[S3] Saved: receipts/{tenant_name}/{transaction_id}.json')