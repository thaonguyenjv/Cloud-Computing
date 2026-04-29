# 🏪 SaaS Point-of-Sale (PoS) Application

A multi-tenant web-based Point-of-Sale system built with Flask.
Demo:  https://cloud-computing-production-1636.up.railway.app
> ⚠️ **Note:** Demo hosted on Railway free trial (expires ~24/5/2026)
---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + Flask |
| Database | PostgreSQL (Railway) |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Email | Flask-Mail + Gmail SMTP |
| Frontend | HTML5 + Bootstrap 5 + Vanilla JS |
| Deployment | Railway |

---

## 📁 Project Structure

```
Cloud-Computing/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── products.py
│   │   └── transactions.py
│   └── templates/
│       ├── base.html
│       ├── base_auth.html
│       ├── admin/
│       ├── auth/
│       ├── pos/
│       └── product/
├── config.py
├── run.py
├── requirements.txt
├── Procfile
├── railway.toml
└── .env
```

---

## 🚀 Getting Started

```bash
# 1. Clone repository
git clone https://github.com/thaonguyenjv/Cloud-Computing.git
cd Cloud-Computing

# 2. Create & activate virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://...
MAIL_USERNAME=youremail@gmail.com
MAIL_PASSWORD=your-app-password

# 5. Run
python run.py
```

---

## 🔑 Master Admin

```
Email   : masteradmin@pos.com
Password: admin@123
```

## Sample Tenant

```
Email   : cafeshop@gmail.com 
Password: 0987654321
```

```
Email   : fashionng@shop.com
Password: 18082005
```