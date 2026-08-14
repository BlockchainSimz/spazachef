export type SubscriptionTier = 'free' | 'basic' | 'premium';

export interface Chef {
  id: string;
  name: string;
  dialect: string;
  personality: string;
  avatar: string;
  accent: string;
  bio: string;
}

export interface RecipeRequest {
  ingredients: string[];
  chefId: string;
  tier: SubscriptionTier;
}

export interface RecipeResponse {
  recipe: string;
  ingredients: string[];
  instructions: string[];
  followUpQuestionsRemaining: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  chefName?: string;
}
