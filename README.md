# **Course Marketplace Platform: Detailed Project Description**  
This document outlines the functionality, architecture, and logic for the Course Marketplace Platform, enabling creators to monetize content and learners to engage via real-time communication.

---

## **1. Project Overview**  
The platform is a **course marketplace** where:  
- **Creators** (any registered user) can design, publish, and sell courses.  
- **Learners** can discover, purchase, and interact with courses and creators.  
- **Admins** manage platform operations, commissions, and moderation.  

### **Core Features**  
1. **Open Course Creation**: Any user can create and sell courses (free or paid).  
2. **Real-Time Communication**: Integrated chat, direct messaging, and course Q&A.  
3. **Monetization & Commissions**: Platform earns a percentage of paid course sales.  
4. Role-based access (Creator, Learner, Admin) with flexible permissions.  
5. Course discovery with advanced search, filters, and recommendations.  
6. Admin dashboard for financial tracking, user moderation, and dispute resolution.  

---

## **2. Application Logic**  

### **2.1. User Roles and Permissions**  
#### **Creators**  
- Create, edit, and publish courses (free or paid).  
- Set course prices and manage earnings (post-commission).  
- Interact with learners via chat and course discussions.  
- View sales analytics and learner engagement metrics.  

#### **Learners**  
- Browse, purchase, and enroll in courses.  
- Access purchased courses and participate in discussions.  
- Message creators and other learners.  
- Rate courses and leave public reviews.  

#### **Admins**  
- Approve/reject courses to ensure quality and compliance.  
- Manage commissions (e.g., set rates, view transaction history).  
- Moderate chats, resolve disputes, and suspend accounts.  

---

### **2.2. Course Management**  
#### **Course Properties**  
- **Price**: Free or set amount (with platform commission).  
- **Status**: Draft, Under Review (admin approval), Published.  
- **Materials**: Videos, PDFs, quizzes, and discussion boards.  
- **Earnings**: Track revenue (after commission) in creator dashboard.  

#### **Commission Logic**  
- Admins set global commission rates (e.g., 15% per sale).  
- Creators receive earnings post-commission, withdrawable via Stripe/PayPal.  

---

### **2.3. Real-Time Communication**  
- **Course Chat**: Public chat rooms for enrolled learners.  
- **Direct Messaging**: Private conversations between users.  
- **Notifications**: Alerts for new messages, sales, and course updates.  

---

### **2.4. Search and Filtering**  
- **Filters**: Price (free/paid), ratings, category, creator.  
- **Sorting**: Trending (engagement), newest, highest-rated.  

---

### **2.5. Access Control**  
- **Public Access**: Browse courses without an account.  
- **Private Access**:  
  - Purchases and messaging require login.  
  - Creators control course visibility (draft/published).  
- **RBAC**:  
  - Admins approve courses and manage payouts.  
  - Learners cannot edit courses; creators cannot moderate others.  

---

### **2.6. Payments & Payouts**  
- **Stripe/PayPal Integration**: Handle purchases and creator withdrawals.  
- **Escrow System**: Hold earnings until course completion (configurable).  

---

## **3. Development Architecture**  

### **3.1. Backend**  
- **Framework**: Django + Django Channels (WebSocket support).  
- **Authentication**: JWT with OAuth2 for social logins.  
- **Database**: PostgreSQL + Redis (for real-time features).  

#### **APIs**  
- **Course & Payment**: CRUD, purchase, commission calculation.  
- **Chat**: WebSocket endpoints for messaging and notifications.  
- **Admin**: Payout management, dispute resolution, analytics.  

---

### **3.2. Frontend**  
- **Framework**: React.js (Next.js for SSR) + Tailwind CSS.  
- **Key Pages**:  
  - **Creator Dashboard**: Course stats, earnings, chat inbox.  
  - **Marketplace**: Course listings with filters and recommendations.  
  - **Chat Interface**: Real-time messaging with message history.  

---

### **3.3. Database Design**  
| **Table**         | **Fields**                                                                 |  
| ----------------- | -------------------------------------------------------------------------- |  
| **User**          | ID, email, role, stripe_account_id, balance, created_at                    |  
| **Course**        | ID, title, price, commission_rate, status (draft/published), creator_id   |  
| **Enrollment**    | ID, course_id, learner_id, purchased_at, payment_status                   |  
| **Message**       | ID, sender_id, receiver_id, content, timestamp, is_read                   |  
| **Transaction**   | ID, course_id, learner_id, amount, commission, payout_date                |  

---

## **4. Questions Answered**  
1. **How do commissions work?**  
   - Admins set a global rate (e.g., 15%). Creators earn the remaining 85% per sale.  

2. **Can users be both creators and learners?**  
   - Yes! Users switch roles seamlessly via their dashboard.  

3. **How is real-time chat implemented?**  
   - WebSockets (Django Channels) power instant messaging and notifications.  

4. **How are payments processed?**  
   - Stripe/PayPal handles purchases. Creators withdraw earnings via linked accounts.  

5. **Are courses moderated?**  
   - Yes. Admins review courses before publication to ensure quality.  

---

## **5. Deployment Strategy**  
1. **Backend**: Dockerized Django + Gunicorn on AWS EC2.  
2. **Frontend**: Vercel for Next.js static hosting.  
3. **Real-Time**: Redis cluster for WebSocket management.  
4. **Database**: AWS RDS (PostgreSQL) with daily backups.  

---

## **6. Future Enhancements**  
1. **Affiliate Program**: Users earn by promoting courses.  
2. **Live Workshops**: Integrate Zoom/Google Meet for live sessions.  
3. **Mobile App**: Flutter-based app for on-the-go learning.  
4. **AI Recommendations**: Suggest courses based on user behavior.  


# Course Marketplace Platform

## Overview
The **Course Marketplace Platform** enables users to create, sell, and purchase courses while providing real-time communication between learners and creators. The platform consists of a **Django backend** and a **Vue frontend**.

## Table of Contents
- [Backend (Django)](local-README.md#backend-django)
- [Frontend (Vue)](local-README.md#frontend-vue)
- [Installation Guide](local-README.md#installation-guide)
- [Deployment](local-README.md#deployment)
- [Future Enhancements](local-README.md#future-enhancements)

---

## Backend (Django)
The backend is built using **Django** and **Django Channels** to support real-time features like chat and notifications.

### Features
- User authentication (JWT-based with OAuth2 support)
- Course management (CRUD operations for courses)
- Payment processing (Stripe/PayPal)
- WebSockets for real-time messaging
- Role-based access control (Creator, Learner, Admin)
- PostgreSQL database with Redis for real-time operations

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-repo/course-marketplace.git
   cd course-marketplace/backend
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   Create a `.env` file in the root of the backend directory and add the following:
   ```sh
   SECRET_KEY=your_secret_key
   DEBUG=True
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=localhost
   DB_PORT=5432
   ```
5. **Run migrations:**
   ```sh
   python manage.py migrate
   ```
6. **Create a superuser (for admin access):**
   ```sh
   python manage.py createsuperuser
   ```
7. **Run the server:**
   ```sh
   python manage.py runserver
   ```

---

## Frontend (Vue)
The frontend is built using **Vue.js** and interacts with the Django backend via REST API.

### Features
- Course listing and search with filters
- Secure authentication via JWT
- Payment integration
- Real-time chat with WebSocket support
- User dashboards (Creator, Learner, Admin)

### Installation
1. **Navigate to the frontend directory:**
   ```sh
   cd ../frontend
   ```
2. **Install dependencies:**
   ```sh
   npm install
   ```
3. **Set up environment variables:**
   Create a `.env` file in the root of the frontend directory and add:
   ```sh
   VUE_APP_API_BASE_URL=http://127.0.0.1:8000/api
   ```
4. **Run the development server:**
   ```sh
   npm run serve
   ```

---

## Deployment

### Backend Deployment
- Use **Gunicorn + Nginx** for production.
- Deploy on **AWS EC2 / DigitalOcean**.
- Set up **PostgreSQL on AWS RDS**.
- Use **Redis for WebSocket support**.

### Frontend Deployment
- Deploy on **Vercel / Netlify**.
- Configure `.env.production` for API connection.
- Use **Cloudflare for caching and security**.

---

## Future Enhancements
- Mobile app using **Flutter**.
- AI-based course recommendations.
- Affiliate marketing system for course promotions.
- Live workshops via **Zoom/Google Meet integration**.

---

For further details, please check the backend and frontend README files inside their respective directories.
