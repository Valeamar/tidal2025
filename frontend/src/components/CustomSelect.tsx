import React, { useState, useRef, useEffect } from 'react';

interface CustomSelectProps {
    id?: string;
    value: string;
    onChange: (value: string) => void;
    options: string[];
    placeholder?: string;
    className?: string;
    error?: boolean;
}

const CustomSelect: React.FC<CustomSelectProps> = ({
    id,
    value,
    onChange,
    options,
    placeholder = "Select option",
    className = "",
    error = false
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [highlightedIndex, setHighlightedIndex] = useState(-1);
    const selectRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        if (!isOpen) {
            setHighlightedIndex(-1);
        }
    }, [isOpen]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (!isOpen) {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
                e.preventDefault();
                setIsOpen(true);
            }
            return;
        }

        switch (e.key) {
            case 'Escape':
                setIsOpen(false);
                break;
            case 'ArrowDown':
                e.preventDefault();
                setHighlightedIndex(prev =>
                    prev < options.length - 1 ? prev + 1 : 0
                );
                break;
            case 'ArrowUp':
                e.preventDefault();
                setHighlightedIndex(prev =>
                    prev > 0 ? prev - 1 : options.length - 1
                );
                break;
            case 'Enter':
                e.preventDefault();
                if (highlightedIndex >= 0) {
                    onChange(options[highlightedIndex]);
                    setIsOpen(false);
                }
                break;
        }
    };

    const handleOptionClick = (option: string) => {
        onChange(option);
        setIsOpen(false);
    };

    const displayValue = value || placeholder;
    const isPlaceholder = !value;

    return (
        <div
            ref={selectRef}
            className={`relative ${className}`}
        >
            <div
                id={id}
                role="combobox"
                aria-expanded={isOpen}
                aria-haspopup="listbox"
                tabIndex={0}
                onClick={() => setIsOpen(!isOpen)}
                onKeyDown={handleKeyDown}
                className={`
          modern-input w-full cursor-pointer flex items-center justify-between
          ${error ? 'border-red-400 bg-red-500/10' : ''}
          ${isOpen ? 'border-accent-400 shadow-glow' : ''}
        `}
            >
                <span className={isPlaceholder ? 'text-white/60' : 'text-white'}>
                    {displayValue}
                </span>
                <svg
                    className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </div>

            {isOpen && (
                <div className="absolute z-50 w-full mt-2 glass-card border-accent-400/30 max-h-60 overflow-y-auto">
                    <ul role="listbox" className="py-2">
                        {options.map((option, index) => (
                            <li
                                key={option}
                                role="option"
                                aria-selected={value === option}
                                onClick={() => handleOptionClick(option)}
                                onMouseEnter={() => setHighlightedIndex(index)}
                                className={`
                  px-4 py-3 cursor-pointer transition-all duration-200 text-white
                  ${value === option
                                        ? 'bg-gradient-accent text-white font-medium'
                                        : highlightedIndex === index
                                            ? 'bg-white/20'
                                            : 'hover:bg-white/10'
                                    }
                `}
                            >
                                {option}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default CustomSelect;