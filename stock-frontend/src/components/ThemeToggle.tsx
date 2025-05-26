import { useEffect, useState } from 'react';

export default function ThemeToggle() {
  const [mode, setMode] = useState<'light' | 'dark'>(() =>
    localStorage.getItem('theme') === 'dark' ? 'dark' : 'light'
  );

  useEffect(() => {
    document.documentElement.classList.toggle('dark', mode === 'dark');
    localStorage.setItem('theme', mode);
  }, [mode]);

  return (
    <button
      style={{ top: 'clamp(1rem, 5vh, 2.5rem)', color: 'black' }}
      onClick={() => setMode(prev => (prev === 'dark' ? 'light' : 'dark'))}
      className="fixed top-2 -mt-2 right-4 z-[9999] bg-gray-200 dark:bg-white text-black p-2 rounded"
    >
      <span className="text-black">
        {mode === 'dark' ? '🌞 Light Mode' : '🌙 Dark Mode'}
      </span>
    </button>
  );
}
