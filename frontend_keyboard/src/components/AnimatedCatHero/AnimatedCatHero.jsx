function AnimatedCatHero() {
    return (
        <div className="cat-hero" aria-label="Animated curious cat with books">
            <svg className="cat-hero-svg" viewBox="0 0 520 520" role="img">
                <defs>
                    <radialGradient id="catAura" cx="50%" cy="45%" r="62%">
                        <stop offset="0%" stopColor="#ffffff" stopOpacity="0.96" />
                        <stop offset="62%" stopColor="#f7f4ff" stopOpacity="0.78" />
                        <stop offset="100%" stopColor="#dff8f3" stopOpacity="0.2" />
                    </radialGradient>
                    <linearGradient id="catFur" x1="23%" x2="83%" y1="8%" y2="92%">
                        <stop offset="0%" stopColor="#2b2450" />
                        <stop offset="45%" stopColor="#6a4bd8" />
                        <stop offset="100%" stopColor="#23a7b6" />
                    </linearGradient>
                    <linearGradient id="catBelly" x1="10%" x2="95%" y1="10%" y2="92%">
                        <stop offset="0%" stopColor="#fff7fd" />
                        <stop offset="100%" stopColor="#c8f7ee" />
                    </linearGradient>
                    <linearGradient id="catLaptop" x1="6%" x2="100%" y1="12%" y2="96%">
                        <stop offset="0%" stopColor="#ff8bc8" />
                        <stop offset="100%" stopColor="#4db7dc" />
                    </linearGradient>
                    <filter id="catSoftShadow" x="-30%" y="-30%" width="160%" height="170%">
                        <feDropShadow dx="0" dy="20" stdDeviation="18" floodColor="#3a3658" floodOpacity="0.22" />
                    </filter>
                </defs>

                <circle className="cat-aura" cx="260" cy="260" r="214" fill="url(#catAura)" />
                <circle className="cat-ring" cx="260" cy="260" r="220" />

                <g className="cat-stars">
                    <path className="cat-spark cat-spark-one" d="M97 114l16 38 38 16-38 16-16 38-16-38-38-16 38-16 16-38Z" />
                    <path className="cat-spark cat-spark-two" d="M425 345l13 31 31 13-31 13-13 31-13-31-31-13 31-13 13-31Z" />
                    <path className="cat-spark cat-spark-three" d="M396 98l8 19 19 8-19 8-8 19-8-19-19-8 19-8 8-19Z" />
                </g>

                <g className="cat-book cat-book-left">
                    <path d="M88 315c26-17 52-18 78-1v45c-26-17-52-16-78 2v-46Z" fill="#84e5e0" />
                    <path d="M166 314c21-14 43-14 67 0v45c-24-14-46-14-67 0v-45Z" fill="#f7e48d" />
                    <path d="M166 314v45" stroke="#293044" strokeWidth="4" />
                    <path d="M102 327c16-6 32-6 48 0M102 341c17-5 33-5 48 0M182 327c13-5 26-5 39 0M182 342c13-4 26-4 39 0" stroke="#293044" strokeOpacity="0.5" strokeWidth="3" strokeLinecap="round" />
                </g>

                <g className="cat-book cat-book-right">
                    <path d="M370 156c19-18 41-24 65-18l11 40c-25-7-47-1-66 17l-10-39Z" fill="#ff85bd" />
                    <path d="M351 151c-22-7-42-4-60 10l11 40c18-13 38-16 60-9l-11-41Z" fill="#66d8e6" />
                    <path d="M362 151l10 41" stroke="#293044" strokeWidth="4" />
                    <path d="M304 171c13-5 25-7 37-5M309 184c13-5 25-6 36-4M386 158c12-4 24-4 36 0M390 173c12-4 24-4 36 0" stroke="#293044" strokeOpacity="0.5" strokeWidth="3" strokeLinecap="round" />
                </g>

                <ellipse className="cat-shadow" cx="266" cy="405" rx="132" ry="20" fill="#141827" opacity="0.18" />

                <g className="cat-body" filter="url(#catSoftShadow)">
                    <path className="cat-tail" d="M352 306c69 0 94 44 65 84-18 26-57 24-70 3 28 4 45-13 39-31-8-24-48-17-56-47" fill="none" stroke="#2f2854" strokeWidth="31" strokeLinecap="round" />
                    <path d="M206 237c-23 30-37 77-30 117 8 46 41 72 91 72 54 0 88-28 95-76 6-40-7-84-33-113H206Z" fill="url(#catFur)" />
                    <path d="M224 271c-14 24-21 58-16 88 5 31 26 48 59 48 35 0 57-19 61-51 4-29-3-62-18-85H224Z" fill="url(#catBelly)" opacity="0.9" />

                    <g className="cat-head">
                        <path d="M181 137l-36-45-5 71c-17 22-25 49-22 78 7 65 66 101 143 101 79 0 137-37 143-103 3-30-6-58-24-80l-6-67-35 44c-23-11-51-17-80-17-28 0-55 6-78 18Z" fill="url(#catFur)" />
                        <path d="M151 110l25 40c-11 8-20 18-27 30l2-70ZM370 110l-25 40c12 8 21 18 28 30l-3-70Z" fill="#ffd6e9" opacity="0.9" />
                        <path d="M192 228c-27-3-50-19-50-42 0-22 20-38 48-38 35 0 58 23 65 58-16 16-36 24-63 22ZM329 228c27-3 50-19 50-42 0-22-20-38-48-38-35 0-58 23-65 58 16 16 36 24 63 22Z" fill="#eff8ff" />
                        <g className="cat-eyes">
                            <ellipse cx="191" cy="188" rx="20" ry="29" fill="#121623" />
                            <ellipse cx="329" cy="188" rx="20" ry="29" fill="#121623" />
                            <circle cx="183" cy="176" r="6" fill="#fff" />
                            <circle cx="321" cy="176" r="6" fill="#fff" />
                            <path d="M171 212c11 10 29 10 40 0M309 212c11 10 29 10 40 0" stroke="#ff78a6" strokeWidth="6" strokeLinecap="round" />
                        </g>
                        <path d="M260 220l-13 15h26l-13-15Z" fill="#151927" />
                        <path d="M260 236c-4 13-16 20-30 19M260 236c4 13 16 20 30 19" stroke="#151927" strokeWidth="5" strokeLinecap="round" />
                        <path className="cat-whiskers" d="M151 235c-26-4-47-1-64 9M155 253c-27 6-48 17-63 32M369 235c26-4 47-1 64 9M365 253c27 6 48 17 63 32" stroke="#293044" strokeWidth="5" strokeLinecap="round" opacity="0.55" />
                    </g>

                    <g className="cat-paws">
                        <ellipse cx="209" cy="348" rx="27" ry="17" fill="#fff4fb" />
                        <ellipse cx="315" cy="348" rx="27" ry="17" fill="#fff4fb" />
                    </g>

                    <g className="cat-laptop">
                        <path d="M166 313h180l-20 72H186l-20-72Z" fill="url(#catLaptop)" />
                        <path d="M186 385h140l28 22H159l27-22Z" fill="#273047" />
                        <circle cx="256" cy="349" r="20" fill="#e8ffff" opacity="0.75" />
                        <circle className="cat-laptop-light" cx="256" cy="349" r="10" fill="#49dced" />
                    </g>
                </g>

                <g className="cat-dots">
                    <circle cx="112" cy="271" r="8" />
                    <circle cx="404" cy="270" r="6" />
                    <circle cx="145" cy="364" r="5" />
                </g>
            </svg>
        </div>
    );
}

export default AnimatedCatHero;
