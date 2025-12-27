# 🚗 Vehicle Parking Management System

A full-stack **Vehicle Parking Management System** developed as part of the **Modern Application Development II (MAD II)** course.  
The application provides a role-based parking solution with real-time slot availability, secure authentication, reservation management, and administrative controls.

---

## 📌 Project Overview

The Vehicle Parking App is designed to digitize and automate parking operations by enabling users to:
- View available parking lots and slots
- Reserve parking spaces
- Manage reservations
- Download parking history
- Provide administrators full control over parking infrastructure

The system follows a **RESTful architecture** with a secure backend and a responsive frontend.

---

## 🛠️ Tech Stack

### 🔹 Backend
- **Flask** (Python)
- **Flask-RESTful**
- **Flask-JWT-Extended** (Authentication & Authorization)
- **SQLite / SQLAlchemy ORM**
- **CSV Export Utility**

### 🔹 Frontend
- **Vue.js**
- **Bootstrap**
- **Axios** (API communication)

### 🔹 Tools & Concepts
- REST APIs
- Role-Based Access Control (RBAC)
- JWT Authentication
- Modular MVC Architecture
- Git & GitHub Version Control

---

## 👥 User Roles

### 👤 User
- Signup & Login (JWT based)
- View parking lots and available slots
- Reserve parking slots
- Cancel reservations
- View reservation history
- Export parking history as CSV

### 👨‍💼 Admin
- Create, update, and delete parking lots
- Manage parking slots dynamically
- Monitor overall parking usage
- View system summary and statistics
- Control users and reservations

---

## ⚙️ Core Features

- 🔐 Secure Authentication using JWT
- 🅿️ Real-time Parking Slot Availability
- 📅 Reservation Management System
- 📊 Admin Dashboard & Summary APIs
- 📥 CSV Export of Parking Records
- 🔄 RESTful API-based Architecture
- 📱 Responsive UI Design

Here’s a **clean, technical, and README-ready section** you can **append** to your existing `README.md` to document the **Payment functionality** clearly.

You can paste this **after “Core Features” or before “Project Structure”**.

---

## 💳 Payment & Billing Functionality

The Vehicle Parking Management System includes a **Payment module** that allows users to view their pending parking dues and complete payments seamlessly using **UPI-based digital payments**.

### 🔹 Payment Workflow (User Side)

* Each user can access a dedicated **Payments tab** from the dashboard.
* The system calculates the **due amount** based on:

  * Reservation duration
  * Parking slot pricing
  * Active or completed reservations
* The due amount is displayed in real time on the Payments screen.
* Users can initiate payment via **UPI** using an integrated payment link or QR-based redirection.
* Once the payment is completed:

  * The transaction status is updated
  * The due amount is cleared
  * Payment records are stored for future reference

### 🔹 Payment Features

* 💰 Real-time due amount calculation
* 📱 UPI-based payment redirection (PhonePe / Google Pay / Paytm supported)
* 🔗 Secure payment link generation
* 🧾 Payment status tracking
* 📊 Payment history visibility (future scope)
* 🔐 User-specific payment access (JWT protected)

### 🔹 Security & Access Control

* Payments are accessible **only to authenticated users**
* JWT tokens ensure secure API communication
* Users can only view and pay **their own dues**
* Admin access is restricted to monitoring and auditing purposes

### 🔹 Future Enhancements (Planned)

* Online payment gateway integration (Razorpay / Stripe)
* Automatic invoice generation
* Payment failure handling & retries
* Admin-level payment analytics
* Refund handling for cancelled reservations


