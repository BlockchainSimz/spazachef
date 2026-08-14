# SpazaChef AI Agent Features

## Overview

SpazaChef has been completely redesigned into a Claude-like landing page with an interactive AI Chef Agent system. Users can now generate authentic South African recipes using their available ingredients, with interactive follow-up questions based on their subscription tier.

## Architecture

### Frontend Components

#### `Landing.tsx`
- Claude-like minimal landing page
- Features section highlighting AI Chef Assistant, Interactive Recipes, and Authentic Recipes
- Pricing section with Free (R0), Basic (R15), and Premium (R99) tiers
- Smooth scroll to Recipe Agent interface
- SpazaChef logo and branding

#### `RecipeAgent.tsx`
- Interactive recipe generation interface
- Chef selection screen with 5 personalities
- Real-time chat interface
- Subscription tier tracking for follow-up questions
- Context-aware input handling

#### `SpazaChefLogo.tsx`
- Custom SVG logo with pot and steam elements
- Orange (#B85C2C) and burnt orange (#EA580C) color scheme
- Scalable to any size

### Backend Components

#### Chef Agent (`app/agents/chef_agent.py`)
- 5 distinct South African chef personalities
- Each with unique dialect, personality, and accent
- Prompt engineering for authentic responses
- Mock recipe generation system
- Follow-up question handling

#### API Routes (`app/api/recipes_agent.py`)
- `/api/v1/recipes/generate` - Generate recipe from ingredients
- `/api/v1/recipes/followup` - Handle follow-up questions
- `/api/v1/recipes/health` - Health check

## Chef Personalities

### 1. Gogo Precious 👵
- **Dialect**: South African Zulu/Sotho
- **Personality**: Warm, motherly, uses "hey my child", "eish"
- **Accent**: "Hey my child, this one is gonna make your belly happy, hai!"
- **Bio**: The grandmother of kasi cooking. Knows every shortcut and story.

### 2. Chef Mandla 👨‍🍳
- **Dialect**: Johannesburg Kasi
- **Personality**: Cool, confident, street-smart, says "bra", "isit"
- **Accent**: "Eish bra, this recipe is proper hectic! Ay, yebo!"
- **Bio**: The young innovator. Makes magic from what's in the cupboard.

### 3. Tandie the Baker 👩‍🍳
- **Dialect**: Cape Town Vernacular
- **Personality**: Creative, playful, uses "hey-hey", "nogal"
- **Accent**: "Listen here hey-hey, this gonna be lekker goed, nogal!"
- **Bio**: The creative one. Bakes bread that makes people cry happy tears.

### 4. Baba Thabo 🧔
- **Dialect**: Traditional South African
- **Personality**: Wise, traditional, patient, teaches life lessons
- **Accent**: "Ayoba my friend, this recipe, it teaches us about patience and respect."
- **Bio**: The traditionalist. Every recipe comes with wisdom and history.

### 5. Chef Zama 👩‍🍳
- **Dialect**: Modern Kasi
- **Personality**: Energetic, funny, says "haibo", uses lots of humor
- **Accent**: "Haibo! This recipe is gonna have your family asking 'who cooked this?'"
- **Bio**: The funny one. Makes cooking entertaining and stress-free.

## Subscription Tiers

### Free (R0/month)
- ✅ 2 follow-up questions per recipe
- ✅ 5 personal chef personalities
- ✅ Save recipes
- ❌ Ads shown

### Basic (R15/month)
- ✅ 5 follow-up questions per recipe
- ✅ All Free features
- ✅ Ad-free experience
- ✅ Offline access

### Premium (R99/month)
- ✅ Unlimited follow-up questions
- ✅ All Basic features
- ✅ Chef consultations
- ✅ Custom meal plans
- ✅ API access

## User Flow

1. **Landing Page**
   - User visits SpazaChef landing page
   - Sees Claude-like minimal design
   - Reads about features and pricing
   - Clicks "Start Creating Recipes"

2. **Chef Selection**
   - User sees 5 chef personalities
   - Each chef has description, dialect, and accent
   - User clicks to select their preferred chef
   - Chef introduces themselves

3. **Ingredient Input**
   - User enters ingredients they have
   - Can be comma-separated or line-separated
   - User clicks "Generate Recipe"

4. **Recipe Generation**
   - Backend generates recipe using chef's personality
   - Recipe appears in chat interface
   - Chef explains the recipe with personality
   - Follow-up questions become available

5. **Follow-Up Questions**
   - User asks questions about the recipe
   - Questions about substitutions, techniques, timing, etc.
   - Chef answers in character
   - Question counter shows remaining for tier

## Technical Details

### Frontend Stack
- React 19 with TypeScript
- Tailwind CSS for styling
- Lucide icons for UI elements
- Vite build system

### Backend Stack
- FastAPI for API
- Pydantic for data validation
- CORS enabled for frontend communication
- Async/await for all operations

### API Communication
```typescript
// Recipe generation request
POST /api/v1/recipes/generate
{
  "ingredients": ["onion", "tomato", "rice"],
  "chef_id": "gogo-precious",
  "chef_name": "Gogo Precious"
}

// Follow-up question request
POST /api/v1/recipes/followup
{
  "question": "Can I use...?",
  "chef_id": "mandla",
  "chef_name": "Chef Mandla"
}
```

## Deployment Notes

### Frontend
- No changes needed for Vercel deployment
- All components use standard React patterns
- CSS is handled via Tailwind utilities
- API calls use `VITE_API_URL` environment variable

### Backend
- New modules under `app/agents/` and `app/api/`
- Fully async implementation
- No database changes needed
- Mock responses for demonstration

## Future Enhancements

1. **Claude API Integration**
   - Replace mock responses with real Anthropic API calls
   - Use structured outputs for consistent JSON responses
   - Implement streaming responses for real-time generation

2. **Database Integration**
   - Store conversation history per user
   - Track follow-up questions used
   - Save favorite recipes to database

3. **User Authentication**
   - Link recipes to user accounts
   - Track subscription tier
   - Implement payment processing via PayFast

4. **Advanced Features**
   - Recipe rating and reviews
   - Community recipes sharing
   - Dietary preferences (vegan, halal, kosher)
   - Allergen tracking
   - Meal plan generation
   - Nutrition information

## Code Organization

```
frontend/src/
├── pages/
│   └── Landing.tsx          # Main landing page
├── components/
│   ├── SpazaChefLogo.tsx   # Custom logo
│   └── RecipeAgent.tsx      # Main agent component
├── types/
│   └── chef.ts              # TypeScript types
└── lib/
    └── chefs.ts             # Chef data and prompts

backend/app/
├── agents/
│   └── chef_agent.py        # Chef personality logic
├── api/
│   └── recipes_agent.py     # API endpoints
├── config.py                # Configuration
└── main.py                  # FastAPI app
```

## Testing the Agent

### 1. Local Development
```bash
# Frontend
cd frontend && npm run dev

# Backend
cd backend && python -m uvicorn app.main:app --reload
```

### 2. Test Recipe Generation
```bash
curl -X POST http://localhost:8000/api/v1/recipes/generate \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["onion", "tomato", "rice"],
    "chef_id": "gogo-precious",
    "chef_name": "Gogo Precious"
  }'
```

### 3. Test Follow-Up
```bash
curl -X POST http://localhost:8000/api/v1/recipes/followup \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can I make this without onions?",
    "chef_id": "mandla",
    "chef_name": "Chef Mandla"
  }'
```

## Performance & Optimization

- Lazy loading of RecipeAgent component
- Message virtualization for long conversations
- Smooth animations and transitions
- Responsive design for mobile, tablet, desktop
- Zero-JavaScript fallback for CSS styling

## Accessibility

- Semantic HTML throughout
- ARIA labels on interactive elements
- Keyboard navigation support
- Color contrast meets WCAG AA standards
- Focus indicators on all interactive elements

