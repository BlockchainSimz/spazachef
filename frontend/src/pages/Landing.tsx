import React, { useState, useRef } from 'react';
import { ArrowRight, Zap, MessageCircle, Lock } from 'lucide-react';
import RecipeAgent from '../components/RecipeAgent';
import SpazaChefLogo from '../components/SpazaChefLogo';

const Landing: React.FC = () => {
  const [showAgent, setShowAgent] = useState(false);
  const agentRef = useRef<HTMLDivElement>(null);

  const scrollToAgent = () => {
    setShowAgent(true);
    setTimeout(() => {
      agentRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-orange-50 to-stone-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-stone-200 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SpazaChefLogo size={32} />
            <span className="text-xl font-bold text-stone-900">SpazaChef</span>
          </div>
          <button
            onClick={scrollToAgent}
            className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition"
          >
            Start Cooking
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8 inline-block">
            <SpazaChefLogo size={80} />
          </div>
          
          <h1 className="text-6xl font-bold text-stone-900 mb-6">
            Cook South African
            <span className="block text-orange-600">with Your Ingredients</span>
          </h1>
          
          <p className="text-xl text-stone-600 mb-8 max-w-2xl mx-auto">
            Meet your personal kasi chef. Tell them what you have, and they'll create authentic South African recipes just for you. Fresh. Real. Delicious.
          </p>

          <button
            onClick={scrollToAgent}
            className="inline-flex items-center gap-2 px-8 py-4 bg-orange-600 text-white text-lg font-semibold rounded-lg hover:bg-orange-700 transition group"
          >
            Start Creating Recipes
            <ArrowRight className="group-hover:translate-x-1 transition" size={20} />
          </button>

          <p className="text-sm text-stone-500 mt-4">
            Free tier: Ask 2 follow-up questions • No credit card required
          </p>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-white/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-stone-900 mb-16">
            Features
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-8 bg-white rounded-lg border border-stone-200 hover:border-orange-300 transition">
              <Zap className="text-orange-600 mb-4" size={32} />
              <h3 className="text-xl font-semibold text-stone-900 mb-3">AI Chef Assistant</h3>
              <p className="text-stone-600">
                5 personal South African chefs with authentic dialect. They know how to make magic from what you have.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-8 bg-white rounded-lg border border-stone-200 hover:border-orange-300 transition">
              <MessageCircle className="text-orange-600 mb-4" size={32} />
              <h3 className="text-xl font-semibold text-stone-900 mb-3">Interactive Recipes</h3>
              <p className="text-stone-600">
                Ask follow-up questions to refine your recipe. Get cooking tips, variations, and substitutions instantly.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-8 bg-white rounded-lg border border-stone-200 hover:border-orange-300 transition">
              <Lock className="text-orange-600 mb-4" size={32} />
              <h3 className="text-xl font-semibold text-stone-900 mb-3">Authentic Recipes</h3>
              <p className="text-stone-600">
                All recipes are inspired by South African kasi cuisine. Real flavors. Real techniques. Real results.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-stone-900 mb-16">
            Simple Pricing
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Free Tier */}
            <div className="p-8 bg-white rounded-lg border border-stone-200">
              <h3 className="text-2xl font-bold text-stone-900 mb-2">Free</h3>
              <p className="text-4xl font-bold text-orange-600 mb-6">R0<span className="text-sm text-stone-600">/month</span></p>
              
              <ul className="space-y-3 mb-8 text-stone-600">
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  2 follow-up questions per recipe
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  5 personal chef personalities
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  Save recipes
                </li>
              </ul>

              <button className="w-full py-2 border border-orange-600 text-orange-600 rounded-lg hover:bg-orange-50 transition">
                Start Free
              </button>
            </div>

            {/* Basic Tier */}
            <div className="p-8 bg-orange-600 text-white rounded-lg border-2 border-orange-600 relative transform md:scale-105">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-orange-600 px-4 py-1 rounded-full text-sm font-semibold">
                Popular
              </div>
              
              <h3 className="text-2xl font-bold mb-2">Basic</h3>
              <p className="text-4xl font-bold mb-6">R15<span className="text-sm">/month</span></p>
              
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  5 follow-up questions per recipe
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  All Free features
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  Ad-free experience
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  Offline access
                </li>
              </ul>

              <button className="w-full py-2 bg-white text-orange-600 rounded-lg hover:bg-orange-50 transition font-semibold">
                Upgrade to Basic
              </button>
            </div>

            {/* Premium Tier */}
            <div className="p-8 bg-white rounded-lg border border-stone-200">
              <h3 className="text-2xl font-bold text-stone-900 mb-2">Premium</h3>
              <p className="text-4xl font-bold text-orange-600 mb-6">R99<span className="text-sm text-stone-600">/month</span></p>
              
              <ul className="space-y-3 mb-8 text-stone-600">
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  Unlimited follow-up questions
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  All Basic features
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  Chef consultations
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  Custom meal plans
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-orange-200 flex items-center justify-center text-orange-600 text-sm">✓</span>
                  API access
                </li>
              </ul>

              <button className="w-full py-2 border border-orange-600 text-orange-600 rounded-lg hover:bg-orange-50 transition">
                Upgrade to Premium
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-stone-900 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to cook?</h2>
          <p className="text-xl text-stone-300 mb-8">
            Tell your personal chef what ingredients you have. They'll create magic.
          </p>
          <button
            onClick={scrollToAgent}
            className="inline-flex items-center gap-2 px-8 py-4 bg-orange-600 text-white text-lg font-semibold rounded-lg hover:bg-orange-700 transition group"
          >
            Create Your First Recipe
            <ArrowRight className="group-hover:translate-x-1 transition" size={20} />
          </button>
        </div>
      </section>

      {/* Recipe Agent */}
      {showAgent && (
        <section ref={agentRef} className="py-20 px-6 bg-white">
          <RecipeAgent tier="free" />
        </section>
      )}

      {/* Footer */}
      <footer className="py-12 px-6 bg-stone-50 border-t border-stone-200">
        <div className="max-w-6xl mx-auto text-center text-stone-600">
          <p>SpazaChef © 2026 • Made with 🍳 in South Africa</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
