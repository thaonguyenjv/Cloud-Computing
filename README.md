# 🏪 SaaS Point-of-Sale (PoS) Application

A multi-tenant web-based Point-of-Sale system built with Flask.
**🌐 Live Demo (AWS):** `http://pos-g8-alb-900305759.us-east-1.elb.amazonaws.com`
---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14 + Flask |
| Database | PostgreSQL (AWS RDS) |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Email | Brevo API |
| Storage | AWS S3 |
| Frontend | HTML5 + Bootstrap 5 + Vanilla JS |
| Deployment | AWS EC2 (t3.micro) |
| Networking | AWS VPC + Security Groups |

**AWS Services used:**
- **EC2** — Application server (Ubuntu 24.04, t3.micro)
- **RDS** — PostgreSQL database (db.t4g.micro, private subnet)
- **S3** — Receipt storage 
- **VPC** — Isolated network 
- **IAM** — Role-based access control
- **Application Load Balancer**
- **CloudWatch** — Monitoring and logs

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