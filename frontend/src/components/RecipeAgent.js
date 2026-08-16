import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import React, { useState, useRef, useEffect } from 'react';
import { Send, X, Loader } from 'lucide-react';
import { CHEFS, FOLLOW_UP_QUESTIONS } from '../lib/chefs';
const RecipeAgent = ({ tier = 'free' }) => {
    const [selectedChef, setSelectedChef] = useState(null);
    const [ingredients, setIngredients] = useState('');
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const [followUpQuestionsUsed, setFollowUpQuestionsUsed] = useState(0);
    const [hasRecipeGenerated, setHasRecipeGenerated] = useState(false);
    const messagesEndRef = useRef(null);
    const ingredientsInputRef = useRef(null);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    const handleChefSelect = (chef) => {
        setSelectedChef(chef);
        setMessages([
            {
                role: 'assistant',
                chefName: chef.name,
                content: `${chef.accent}\n\nHey! I'm ${chef.name}. ${chef.bio}\n\nTell me, what ingredients you got, and I'll cook up something lekker for you! Just type them in, and we'll make magic happen.`,
            },
        ]);
    };
    const generateRecipe = async () => {
        if (!ingredients.trim() || !selectedChef)
            return;
        // Add user message
        const userMsg = {
            role: 'user',
            content: `I have these ingredients: ${ingredients}`,
        };
        setMessages((prev) => [...prev, userMsg]);
        setLoading(true);
        try {
            // Call backend API
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/recipes/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ingredients: ingredients.split(',').map((i) => i.trim()),
                    chef_id: selectedChef.id,
                    chef_name: selectedChef.name,
                }),
            });
            const data = await response.json();
            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    chefName: selectedChef.name,
                    content: data.recipe_description,
                },
            ]);
            setHasRecipeGenerated(true);
            setFollowUpQuestionsUsed(0);
            setIngredients('');
        }
        catch (error) {
            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    chefName: selectedChef.name,
                    content: 'Eish, I had a problem there. Try again, hey!',
                },
            ]);
        }
        finally {
            setLoading(false);
        }
    };
    const sendFollowUpQuestion = async () => {
        if (!inputValue.trim() || !selectedChef)
            return;
        const remaining = FOLLOW_UP_QUESTIONS[tier] - followUpQuestionsUsed;
        if (remaining <= 0 && tier !== 'premium') {
            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    chefName: selectedChef.name,
                    content: `Eish, you used all your follow-up questions for now! Upgrade to Basic (R15/month) for 5 questions, or Premium (R99/month) for unlimited. No lies, it's worth it!`,
                },
            ]);
            return;
        }
        const userMsg = {
            role: 'user',
            content: inputValue,
        };
        setMessages((prev) => [...prev, userMsg]);
        setInputValue('');
        setLoading(true);
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/recipes/followup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: inputValue,
                    chef_id: selectedChef.id,
                    chef_name: selectedChef.name,
                }),
            });
            const data = await response.json();
            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    chefName: selectedChef.name,
                    content: data.response,
                },
            ]);
            if (tier !== 'premium') {
                setFollowUpQuestionsUsed(followUpQuestionsUsed + 1);
            }
        }
        catch (error) {
            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    chefName: selectedChef.name,
                    content: 'Eish, something went wrong. Try again, bra!',
                },
            ]);
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("div", { className: "max-w-4xl mx-auto bg-white rounded-lg border border-stone-200 shadow-lg overflow-hidden", children: !selectedChef ? (_jsxs("div", { className: "p-8", children: [_jsx("h2", { className: "text-2xl font-bold text-stone-900 mb-6", children: "Pick Your Personal Chef" }), _jsx("p", { className: "text-stone-600 mb-8", children: "Each chef has their own personality and dialect. Choose who you want to cook with today!" }), _jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: CHEFS.map((chef) => (_jsxs("button", { onClick: () => handleChefSelect(chef), className: "p-6 bg-gradient-to-br from-stone-50 to-orange-50 border-2 border-stone-200 rounded-lg hover:border-orange-400 hover:shadow-md transition text-left", children: [_jsxs("div", { className: "flex items-start justify-between mb-3", children: [_jsx("div", { className: "text-4xl", children: chef.avatar }), _jsx("span", { className: "text-sm text-orange-600 font-semibold", children: chef.dialect })] }), _jsx("h3", { className: "text-lg font-bold text-stone-900 mb-2", children: chef.name }), _jsx("p", { className: "text-sm text-stone-600 mb-3", children: chef.bio }), _jsxs("p", { className: "text-xs italic text-orange-600", children: ["\"", chef.accent, "\""] })] }, chef.id))) })] })) : (_jsxs(_Fragment, { children: [_jsxs("div", { className: "bg-gradient-to-r from-orange-600 to-orange-500 text-white p-6 flex items-center justify-between", children: [_jsxs("div", { className: "flex items-center gap-4", children: [_jsx("span", { className: "text-5xl", children: selectedChef.avatar }), _jsxs("div", { children: [_jsx("h2", { className: "text-2xl font-bold", children: selectedChef.name }), _jsx("p", { className: "text-orange-100", children: selectedChef.dialect })] })] }), _jsx("button", { onClick: () => {
                                setSelectedChef(null);
                                setMessages([]);
                                setIngredients('');
                                setHasRecipeGenerated(false);
                                setFollowUpQuestionsUsed(0);
                            }, className: "p-2 hover:bg-orange-400 rounded-lg transition", children: _jsx(X, { size: 24 }) })] }), _jsxs("div", { className: "h-96 overflow-y-auto p-6 space-y-4 bg-stone-50", children: [messages.map((msg, idx) => (_jsx("div", { className: `flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`, children: _jsxs("div", { className: `max-w-xs lg:max-w-md p-4 rounded-lg ${msg.role === 'user'
                                    ? 'bg-orange-600 text-white'
                                    : 'bg-white text-stone-900 border border-stone-200'}`, children: [msg.role === 'assistant' && (_jsx("p", { className: "text-xs font-semibold text-orange-600 mb-1", children: msg.chefName })), _jsx("p", { className: "text-sm whitespace-pre-wrap", children: msg.content })] }) }, idx))), loading && (_jsx("div", { className: "flex justify-start", children: _jsx("div", { className: "p-4 bg-white rounded-lg border border-stone-200", children: _jsx(Loader, { className: "animate-spin text-orange-600", size: 20 }) }) })), _jsx("div", { ref: messagesEndRef })] }), _jsx("div", { className: "p-6 border-t border-stone-200 bg-white", children: !hasRecipeGenerated ? (_jsxs(_Fragment, { children: [_jsx("label", { className: "block text-sm font-semibold text-stone-900 mb-2", children: "What ingredients you got?" }), _jsx("textarea", { ref: ingredientsInputRef, value: ingredients, onChange: (e) => setIngredients(e.target.value), placeholder: "e.g., onions, tomatoes, rice, chicken, garlic, butter...", className: "w-full p-3 border border-stone-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none", rows: 3, onKeyDown: (e) => {
                                    if (e.key === 'Enter' && e.ctrlKey) {
                                        generateRecipe();
                                    }
                                } }), _jsx("button", { onClick: generateRecipe, disabled: !ingredients.trim() || loading, className: "mt-4 w-full flex items-center justify-center gap-2 px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-stone-400 transition font-semibold", children: loading ? (_jsxs(_Fragment, { children: [_jsx(Loader, { className: "animate-spin", size: 20 }), "Cooking..."] })) : (_jsxs(_Fragment, { children: [_jsx(Send, { size: 20 }), "Generate Recipe"] })) })] })) : (_jsxs(_Fragment, { children: [_jsxs("div", { className: "mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg", children: [tier === 'free' && (_jsxs("p", { className: "text-sm text-stone-700", children: [_jsx("span", { className: "font-semibold", children: "Free Tier:" }), " You have", ' ', _jsx("span", { className: "font-bold text-orange-600", children: Math.max(0, FOLLOW_UP_QUESTIONS[tier] - followUpQuestionsUsed) }), ' ', "follow-up questions left.", ' ', _jsx("button", { className: "text-orange-600 font-semibold hover:underline", children: "Upgrade" })] })), tier === 'basic' && (_jsxs("p", { className: "text-sm text-stone-700", children: [_jsx("span", { className: "font-semibold", children: "Basic Tier:" }), " You have", ' ', _jsx("span", { className: "font-bold text-orange-600", children: Math.max(0, FOLLOW_UP_QUESTIONS[tier] - followUpQuestionsUsed) }), ' ', "follow-up questions left."] })), tier === 'premium' && (_jsxs("p", { className: "text-sm text-stone-700", children: [_jsx("span", { className: "font-semibold", children: "Premium Tier:" }), " Unlimited follow-up questions! Ask away, bra!"] }))] }), _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { type: "text", value: inputValue, onChange: (e) => setInputValue(e.target.value), placeholder: "Ask a follow-up question...", className: "flex-1 p-3 border border-stone-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent", onKeyDown: (e) => {
                                            if (e.key === 'Enter') {
                                                sendFollowUpQuestion();
                                            }
                                        }, disabled: loading ||
                                            (tier !== 'premium' &&
                                                followUpQuestionsUsed >=
                                                    FOLLOW_UP_QUESTIONS[tier]) }), _jsx("button", { onClick: sendFollowUpQuestion, disabled: !inputValue.trim() ||
                                            loading ||
                                            (tier !== 'premium' &&
                                                followUpQuestionsUsed >=
                                                    FOLLOW_UP_QUESTIONS[tier]), className: "p-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-stone-400 transition", children: _jsx(Send, { size: 20 }) })] })] })) })] })) }));
};
export default RecipeAgent;
