# Repair Shop Management System

A Django-based web application designed to streamline operations for electronics and general repair shops. The system tracks work orders, customer information, product details, repair progress, and technician assignments — all in one place.

🔧 **Built for efficiency, transparency, and accountability in repair workflows.**

---

## 📋 Features

- ✅ **Work Order Management**  
  Create, view, update, and close repair jobs with unique tracking IDs.

- ✅ **Customer & Owner Information**  
  Store customer contact details securely.

- ✅ **Product Registration**  
  Log received devices (e.g., laptops, phones, appliances) with model, serial number, and condition.

- ✅ **Problem Description**  
  Record detailed issue reports from customers.

- ✅ **Repair Progress Tracking**  
  Update job status: `Received` → `Diagnosed` → `In Progress` → `Waiting for Parts` → `Completed`.

- ✅ **Technician Assignment**  
  Assign qualified technicians to specific jobs.

- ✅ **RESTful API (via DRF)**  
  Full API support for mobile apps or external integrations.

- ✅ **Admin Dashboard**  
  Built-in Django admin for easy data management.

- ✅ **Search & Filter**  
  Quickly find work orders by ID, customer name, device, or status.

---

## 🛠️ Tech Stack

- **Backend**: Python 3 + Django
- **API**: Django REST Framework (DRF)
- **Database**: PostgreSQL (recommended), SQLite (dev)
- **Frontend**: Django Templates (optional: integrate with React/Vue later)
- **Authentication**: Django built-in (extendable with JWT)
- **Deployment Ready**: Gunicorn, Whitenoise, `.env` support

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
git clone git@github.com:tomibzan/repairshop.git
cd repair-shop