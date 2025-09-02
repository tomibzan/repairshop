# Repair Shop Management System

A Django-based web application to streamline operations for electronics and general repair shops.  
The system manages work orders, customer information, product details, repair progress, and technician assignments.

---

## Features

- Work Order Management: create, view, update, and close repair jobs with unique tracking IDs.
- Customer Information: securely store customer contact details.
- Product Registration: log received devices (laptops, phones, appliances) with model, serial number, and condition.
- Problem Description: record issue reports from customers.
- Repair Progress Tracking: update job status (`Received` → `Diagnosed` → `In Progress` → `Waiting for Parts` → `Completed`).
- Technician Assignment: assign technicians to specific jobs.
- RESTful API (via DRF): endpoints for customers, technicians, and work orders.
- Admin Dashboard: Django admin interface for managing data.
- Search & Filter: find work orders by ID, customer name, device, or status.

---

## Tech Stack

- Backend: Python 3 + Django  
- API: Django REST Framework (DRF)  
- Database: PostgreSQL (recommended), SQLite (development)  
- Frontend: Django Templates (optional future integration with React/Vue)  
- Authentication: Django built-in (extendable with JWT)  
- Environment management: `.env` support  

---

## API Endpoints

Base URL (local): `http://127.0.0.1:8000/api/`  
Base URL (server): `http://ethiofox.click/api/`

**Customers**
- `GET /customers/` – List customers
- `POST /customers/` – Create new customer
- `GET /customers/{id}/` – Retrieve a customer
- `PUT /customers/{id}/` – Update customer
- `DELETE api/customers/{id}/` – Delete customer

**Technicians**
- `GET /technicians/` – List technicians
- `POST /technicians/` – Add technician
- `GET /technicians/{id}/` – Retrieve technician
- `PUT /technicians/{id}/` – Update technician
- `DELETE /technicians/{id}/` – Delete technician

**Work Orders**
- `GET /workorders/` – List work orders
- `POST /workorders/` – Create new work order
- `GET /workorders/{id}/` – Retrieve work order
- `PUT /workorders/{id}/` – Update work order
- `DELETE /workorders/{id}/` – Delete work order

**Images**
- `GET /images/` – List all uploaded images
- `POST /images/` – Upload a new image (attach to work order)
- `GET /images/{id}/` – Retrieve an image
- `DELETE /images/{id}/` – Remove an image

---

## Error Handling

- **400 Bad Request** – invalid input  
- **404 Not Found** – resource not available  
- **500 Internal Server Error** – unexpected issue  

Example:
```json
{
  "detail": "Not found."
}

---


## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
1. git clone git@github.com:tomibzan/repairshop.git
2. cd repair-shop
3. python -m venv venv && source venv/bin/activate
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
5. For testing: cp .env.example .env   
6. python manage.py migrate 
7. python manage.py createsuperuser  -> to explore repairshop backend
8. python manage.py runserver
9. type localhost:8000 in a web browser 
   The project works out-of-the-box with defaults.
If you want custom settings, after copying .env.example to .env edit values.