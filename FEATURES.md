# Subscription Manager Pro - Feature Implementation Guide

## 1. DATA PERSISTENCE ON RENDER.COM (Prevents Data Loss on Commits)

### Problem
Data was being lost when new commits were made because the SQLite database file was not being preserved.

### Solution: Use PostgreSQL Instead of SQLite

**On Render.com:**
1. Create a new PostgreSQL database on Render
2. Copy the `DATABASE_URL` from your Render PostgreSQL instance
3. Set it as an environment variable in your Render app settings
4. The app automatically detects and uses PostgreSQL when `DATABASE_URL` is set

**Environment Variable:**
```
DATABASE_URL=postgresql://username:password@hostname:5432/dbname
```

**How it works:**
- App checks for `DATABASE_URL` environment variable (line 17-25 in app.py)
- If found, uses PostgreSQL (cloud database)
- If not found, uses SQLite for local development
- PostgreSQL persists data indefinitely - it's not in the project files

**Migration from SQLite to PostgreSQL:**
1. Export your current data as JSON:
   ```bash
   curl http://localhost:5000/api/export > backup.json
   ```

2. After setting PostgreSQL on Render:
   - Deploy the app to Render
   - The database schema is created automatically
   - Import your backup:
   ```bash
   curl -X POST https://your-render-app.onrender.com/api/import \
     -H "Content-Type: application/json" \
     -d @backup.json
   ```

---

## 2. PERSON/FAMILY MEMBER FILTERING

### Features Implemented

#### Database Schema
- Added `person_name` field to Subscription model (default: 'Self')
- Stores which family member owns each subscription

#### API Endpoints
- **GET /api/people** - Returns list of all unique family member names
- **GET /api/subscriptions?person=NAME** - Filters subscriptions by person

#### Frontend Features
1. **Person Filter Dropdown**
   - Shows "All People" by default
   - Dynamically populates with family members
   - Filters subscriptions in real-time

2. **Add/Edit Form**
   - New "Person/Family Member" field
   - Input field for entering person's name
   - Defaults to "Self"
   - Examples: "Self", "Mom", "Dad", "Kids", "Wife", etc.

3. **Card Display**
   - Shows person name on each subscription card
   - Allows quick identification of whose subscription it is

### Usage Example
```
Add Subscription:
- Person: "Mom"
- Name: "Netflix"
- Category: OTT
- Cost: 499
- Renewal Date: 2026-10-15

This will only show when filtered by "Mom" or "All People"
```

### Backend Implementation
```python
# Model field
person_name = db.Column(db.String(100), default='Self')

# API endpoint
@app.route('/api/people', methods=['GET'])
def get_people():
    people = db.session.query(Subscription.person_name).distinct().all()
    return jsonify([p[0] for p in people if p[0]])

# Filtering
query = Subscription.query.filter_by(person_name=person) if person else query
```

---

## 3. COMPREHENSIVE BRAND LOGOS FOR ALL SUBSCRIPTIONS

### Logo System

Each subscription has a brand-colored gradient background with an emoji or letter.

#### Entertainment/OTT Services
| Service | Emoji | Color Scheme |
|---------|-------|--------------|
| Netflix | N | Red gradient (#E50914 → #B20710) |
| Prime Video | ▶ | Blue gradient (#00A8E1 → #146EB4) |
| Disney+ | D | Navy gradient (#113CCF → #0F0A5C) |
| Jio Savn | ♪ | Green gradient (#1DB954 → #1AA34A) |
| Hotstar | H | Dark with blue text |
| Sony Liv | S | Black gradient |
| ZEE5 | Z | Purple gradient (#6E3ADB → #8B5CF6) |
| YouTube Premium | ▶ | Red gradient (#FF0000 → #CC0000) |
| Voot | V | Orange gradient (#FF6B00 → #FF8C00) |
| MX Player | M | Dark with pink accent |
| Alt Balaji | A | Orange gradient |
| Apple TV+ | 📺 | Black with tan accent |
| HBO Max | H | Black with purple accent |

#### AI/LLM Services
| Service | Emoji | Color Scheme |
|---------|-------|--------------|
| Claude Pro | C | Indigo gradient (#6366F1 → #8B5CF6) |
| ChatGPT Plus | G | Teal gradient (#10A37F → #0D7D6D) |
| Gemini Pro | ✦ | Google colors (#4285F4 → #EA4335) |
| Copilot Pro | C | Blue gradient (#0078D4 → #005A9E) |
| Midjourney | M | Purple gradient (#9D5BD2 → #6D28D9) |

#### Utilities & Services
| Service | Emoji | Color Scheme |
|---------|-------|--------------|
| Electricity Bill | ⚡ | Gold gradient |
| Water Bill | 💧 | Blue gradient |
| Internet/Broadband | 🌐 | Purple-green gradient |
| Mobile Postpaid | 📱 | Purple gradient |
| Mobile Prepaid | 📱 | Pink-red gradient |
| Gas Bill | 🔥 | Orange-red gradient |
| Car Insurance | 🚗 | Purple gradient |
| Health Insurance | ⚕️ | Teal gradient |
| Gym Membership | 💪 | Red gradient |
| Cloud Storage | ☁️ | Blue gradient |
| Domain Registration | 🌍 | Blue gradient |
| Web Hosting | 🖥️ | Gray gradient |

#### Music & Reading
| Service | Emoji | Color Scheme |
|---------|-------|--------------|
| Spotify | ♫ | Green gradient |
| Apple Music | ♪ | Red gradient |
| Kindle Unlimited | 📚 | Orange gradient |
| Audible | 🎧 | Red-orange gradient |

### Implementation

```javascript
const subscriptionLogos = {
    'Netflix': { 
        emoji: 'N', 
        bg: 'linear-gradient(135deg, #E50914, #B20710)', 
        color: '#fff' 
    },
    // ... more services
};

// Used in card rendering
renderLogoHtml(name) {
    const logo = subscriptionLogos[name];
    return `<div style="background:${logo.bg}; color: ${logo.color}">
        ${logo.emoji}
    </div>`;
}
```

### How to Add New Logos

1. Find the brand's primary colors
2. Create a gradient: `linear-gradient(135deg, PRIMARY, SECONDARY)`
3. Add to `subscriptionLogos` object:

```javascript
'Your Service': { 
    emoji: 'Y',  // or use emoji like '🎮'
    bg: 'linear-gradient(135deg, #COLOR1, #COLOR2)', 
    color: '#ffffff'  // white or black based on bg brightness
}
```

4. The logo automatically displays on subscription cards

---

## Features Summary

### What's New
✅ Data persists on Render.com with PostgreSQL  
✅ Filter subscriptions by family member  
✅ Add person name when creating subscriptions  
✅ Comprehensive brand logos for 40+ services  
✅ Automatic logo coloring based on brand guidelines  

### How to Deploy

**Local Testing:**
```bash
python app.py
# Visit http://localhost:5000
```

**On Render.com:**
1. Connect your GitHub repo
2. Set environment variable: `DATABASE_URL=postgresql://...`
3. Deploy
4. Data will be stored in PostgreSQL and never lost on commits

---

## API Reference

### Endpoints
- `GET /api/subscriptions` - Get all subscriptions
- `GET /api/subscriptions?person=NAME` - Filter by person
- `GET /api/subscriptions?category=OTT` - Filter by category
- `GET /api/people` - Get list of all family members
- `POST /api/subscriptions` - Create subscription
- `PUT /api/subscriptions/:id` - Update subscription
- `DELETE /api/subscriptions/:id` - Delete subscription
- `GET /api/stats` - Get dashboard statistics
- `GET /api/export` - Export all data as JSON
- `POST /api/import` - Import data from JSON

### Request Examples

**Create subscription with person:**
```json
{
    "name": "Netflix",
    "category": "OTT",
    "person_name": "Mom",
    "renewal_date": "2026-10-15",
    "cost": 499,
    "subscription_type": "Monthly",
    "is_recurring": true,
    "reminder_days": 3
}
```

**Get subscriptions for specific person:**
```
GET /api/subscriptions?person=Mom&category=OTT
```

---

## Troubleshooting

### Data Still Being Lost
- Check if `DATABASE_URL` is set in environment
- Verify PostgreSQL credentials are correct
- Export backup: `curl http://localhost:5000/api/export`
- Re-import after fixing database

### Person Filter Not Working
- Ensure you've added `person_name` when creating subscriptions
- Filter dropdown should populate automatically
- Try "All People" if specific person shows no results

### Logos Not Showing
- Check browser console for errors
- Logos are generated with CSS gradients - no images needed
- Falls back to emoji if service name not found

