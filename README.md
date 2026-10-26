# 🏔️ Koraput Tourism — The Heaven of Odisha
### *Full-Fledged Tourism Platform with Mascot Kora, Multi-Image Galleries, Dedicated Admin Portal & AI Tour Guide*

Welcome to the **Koraput Tourism Platform**, an application designed to showcase the beauty, highland majesty, sacred heritage, and indigenous culture of Koraput district, Odisha.

---

## 🌟 Upgraded Highlights & Core Features

### 1. Dedicated Admin Portal (No Navbar Toggle)
- The main website is dedicated exclusively to tourists and travelers.
- Access the administrator workspace at: **`http://localhost:8080/admin/login`** (or via the official footer link).
- Login: `admin` / `koraput2026` (or 1-click Quick Bypass).
- Directs to the **Administration Studio (`/admin`)** with dedicated tabs for:
  - 🏔️ Destinations & Waterfalls
  - 🏨 Stays & Eco-Cottages
  - ☕ Culture, Coffee & Famous Things

### 2. Multi-Image Links for Admin
- Admins can paste multiple image URLs (one per line) when posting destinations, stays, or cultural stories.
- Images are automatically formatted into photo galleries.

### 3. Multi-Image Card Scrolling (Carousel Slider)
- Every card on the homepage and modal view features an interactive image carousel.
- Visitors can click the `<` and `>` arrows or swipe through dot indicators to view all photos directly on the card.

### 4. Dedicated Stays & Eco-Cottages Management
- Form to add and manage nature camps, eco-cottages, homestays, and hotels.
- Captures category, price range, amenities, phone number, booking links, and multiple photos.
- Includes **"⚡ Auto-Refine Stay Story"** using AI to polish raw notes into an inviting description.

### 5. Rich Homepage Lore Managed by Admin
- Dedicated sections for **GI-Tagged Koraput Coffee**, **Living Tribal Culture**, **Famous Delicacies & Handicrafts** (Kotpad dye weaves, Ghatgaon terracotta, Mandia Pej).
- Fully manageable from the admin dashboard with live publishing to the homepage.

### 6. Official Mascot: "KORA — The Spirit of Koraput"
- Integrated the official mascot **Kora** ("Your friendly guide to Nature, Culture & Adventure").
- Featured on the homepage hero greeting card, avatar badges, and the AI assistant.

### 7. "Ask Kora" AI Tour Guide Grounded on Database Records
- Floating **"Ask Kora 🤖"** button in the bottom right corner.
- Powered by a domain-grounded knowledge engine that parses the SQLite database in real time.
- Answers questions about Deomali heights, Duduma timings, entry fees, hotel pricing, tribal culture, and itineraries in Kora's warm persona!

---

## 🚀 How to Run the Application

```powershell
python run_app.py
```
*(Or double-click `run_app.bat`)*

- **Public Tourist Experience:** `http://localhost:8080`
- **Dedicated Admin Portal:** `http://localhost:8080/admin/login`
