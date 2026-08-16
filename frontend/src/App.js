import { jsx as _jsx } from "react/jsx-runtime";
import React from 'react';
import Landing from './pages/Landing';
const App = () => {
    return (_jsx("main", { className: "min-h-screen bg-stone-50", children: _jsx(Landing, {}) }));
};
export default App;
