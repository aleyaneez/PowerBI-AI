import React, { useState, useEffect } from "react";

interface ExamplesProps {
  examples: string[];
  interval?: number;
}

const Examples: React.FC<ExamplesProps> = ({ examples, interval = 5000 }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [animate, setAnimate] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setAnimate(false);
      setTimeout(() => {
        setCurrentIndex(prevIndex => (prevIndex + 1) % examples.length);
        setAnimate(true);
      }, 50);
    }, interval);
    return () => clearInterval(timer);
  }, [examples, interval]);

  return (
    <p className="text-tertiary font-medium text-lg mt-4">
      <span className={`font-bold ${animate ? "animate-bounceIn" : ""}`}>
        {examples[currentIndex]}
      </span>
    </p>
  );
};

export default Examples;