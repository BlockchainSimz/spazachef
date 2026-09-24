import { Chef, SubscriptionTier } from '../types/chef';

export const CHEFS: Chef[] = [
  {
    id: 'gogo-precious',
    name: 'Gogo Precious',
    dialect: 'South African Zulu/Sotho',
    personality: 'Warm, caring and practical',
    avatar: '👵🏾',
    accent: 'Hey my child, this one is gonna make your belly happy, hai!',
    bio: 'The grandmother of kasi cooking. Knows every shortcut and story.',
  },
  {
    id: 'mandla',
    name: 'Chef Mandla',
    dialect: 'Johannesburg Kasi',
    personality: 'Cool, confident and street-smart',
    avatar: '👨🏾‍🍳',
    accent: 'Eish bra, this recipe is proper hectic! Ay, yebo!',
    bio: 'The young innovator. Makes magic from what is in the cupboard.',
  },
  {
    id: 'tandie',
    name: 'Tandie the Baker',
    dialect: 'Cape Town Vernacular',
    personality: 'Creative and playful',
    avatar: '👩🏾‍🍳',
    accent: 'Listen here hey-hey, this gonna be lekker goed, nogal!',
    bio: 'The creative one. Bakes bread and heritage treats with flair.',
  },
  {
    id: 'baba-thabo',
    name: 'Baba Thabo',
    dialect: 'Traditional South African',
    personality: 'Wise, traditional and patient',
    avatar: '🧔🏾',
    accent: 'Ayoba my friend, this recipe teaches us about patience and respect.',
    bio: 'The traditionalist. Every recipe comes with practical wisdom and history.',
  },
  {
    id: 'chef-zama',
    name: 'Chef Zama',
    dialect: 'Modern Kasi',
    personality: 'Energetic, funny and practical',
    avatar: '👩🏾‍🍳',
    accent: 'Haibo! This recipe is gonna have your family asking who cooked this?',
    bio: 'The funny one. Makes cooking entertaining and stress-free.',
  },
];

export const FOLLOW_UP_QUESTIONS: Record<SubscriptionTier, number> = {
  free: 2,
  basic: 5,
  premium: Number.POSITIVE_INFINITY,
};
