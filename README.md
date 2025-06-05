# EduPay: Smart School Payment Management System
EduPay is a modern fintech-powered school payment solution that streamlines tuition fee collection, tracks payment history, and integrates with mobile money and banking APIs. The system empowers schools, parents, and students by providing secure, transparent, and automated financial workflows.

---

## Project Objective

Build a school-centric payment platform with fintech features that enables:

- Parents/students to pay tuition online or via mobile money
- Admins to view real-time payment dashboards
- Automated invoices, reminders, and receipts
- Integration with payment APIs (like Stripe, Flutterwave, or mobile money)
- Role-based access for students, parents, and school accountants

---

## Core Features

| Feature | Description |
|--------|-------------|
| Student Billing System | Generate and assign fee structures per class, term, or student |
| Payment Dashboard | Real-time dashboard showing paid/unpaid invoices |
| Multi-Channel Payment Integration | Integrate APIs like Stripe, PayPal, Flutterwave, or local mobile money |
| Automated Invoices | Send auto-generated bills to parent accounts |
| Receipts & Confirmation | Email or downloadable receipt after successful payment |
| Notifications | Reminders for due/overdue payments |
| Role-Based Access | Separate dashboards for Admin, Accountant, Parent, and Student |
| Transaction History | Full logs with filtering, export, and search capabilities |

---

## Suggested Technology Stack, or any of your choice

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, Tailwind CSS, ShadCN UI |
| Backend | Node.js (Express) or Next.js API Routes |
| Database | PostgreSQL or Supabase |
| Payment API | Stripe, Flutterwave, Paystack, or M-Pesa API |
| Auth | Supabase Auth, Clerk, or Auth0 |
| Deployment | Vercel (frontend), Railway/Render (backend) |

---

## Developer Tasks (Quest Format)

| Task | XP | Description |
|------|----|-------------|
| Set up project and UI layout | 50 | Scaffold Next.js and Tailwind UI |
| Build billing form and fee generator | 100 | Allow admin to input school fees for classes/terms |
| Create invoice generation module | 100 | Automatically generate and assign invoices to students |
| Integrate payment API (e.g. Stripe) | 200 | Allow real transactions and track status |
| Build payment dashboard | 150 | Visualize revenue, unpaid fees, and payment trends |
| Add receipts and confirmation screen | 75 | Show download/printable receipts |
| Set up reminders and email triggers | 100 | Notify parents about due payments |
| Implement role-based dashboards | 150 | Ensure separate views and access rights for each user |
| Add reporting and exports | 75 | Allow CSV/Excel export for accountants |

---

## Getting Started

```bash
npx create-next-app@latest edupay-system
cd edupay-system
npm install tailwindcss zustand axios
