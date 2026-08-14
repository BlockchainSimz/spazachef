import React from 'react';

interface SpazaChefLogoProps {
  size?: number;
}

const SpazaChefLogo: React.FC<SpazaChefLogoProps> = ({ size = 48 }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Pot */}
      <circle cx="50" cy="50" r="35" fill="#B85C2C" opacity="0.1" />
      <path
        d="M30 35 Q30 25 50 25 Q70 25 70 35 L70 65 Q70 75 50 75 Q30 75 30 65 Z"
        fill="#B85C2C"
        stroke="#B85C2C"
        strokeWidth="2"
      />
      
      {/* Handles */}
      <path
        d="M25 45 Q20 45 20 50 Q20 55 25 55"
        stroke="#B85C2C"
        strokeWidth="2"
        fill="none"
      />
      <path
        d="M75 45 Q80 45 80 50 Q80 55 75 55"
        stroke="#B85C2C"
        strokeWidth="2"
        fill="none"
      />
      
      {/* Steam/Fire accent */}
      <path
        d="M45 20 Q42 15 45 10"
        stroke="#EA580C"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M50 20 Q47 15 50 10"
        stroke="#EA580C"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M55 20 Q52 15 55 10"
        stroke="#EA580C"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
      />
    </svg>
  );
};

export default SpazaChefLogo;
