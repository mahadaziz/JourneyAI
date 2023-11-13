"use client";

import {useTheme} from "next-themes";
import { useEffect, useState } from "react";
import { MoonIcon, SunIcon } from '@heroicons/react/24/solid';

const ThemeSwitcher = () => {
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()

  useEffect(() => {
    setMounted(true)
  }, [])

  if(!mounted) return null

  return (
    <div>
        <button
            type="button"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className={`border-1 rounded-md h-10`}
        >
        {theme === "light" ? (
            <MoonIcon className="h-6 w-11  cursor-pointer stroke-1" aria-hidden="true" /> // Moon icon
        ) : (
            <SunIcon className="h-6 w-11  cursor-pointer stroke-1" aria-hidden="true" /> // Sun icon
        )}
        </button>
    </div>
  )
};

export default ThemeSwitcher;