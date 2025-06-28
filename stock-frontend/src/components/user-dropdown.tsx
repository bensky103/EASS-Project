"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Settings, List, LogOut, ChevronDown, User } from "lucide-react"
import { useNavigate } from "react-router-dom"

interface UserDropdownProps {
  user: {
    id: string
    username: string
    email: string
    firstName?: string
    lastName?: string
    profilePicture?: string
  }
  onLogout: () => void
}

export function UserDropdown({ user, onLogout }: UserDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleProfileClick = () => {
    setIsOpen(false)
    navigate(`/profile/${user.id}`)
  }

  const handleWatchlistClick = () => {
    setIsOpen(false)
    navigate(`/watchlist/${user.id}`)
  }

  const handleLogout = () => {
    setIsOpen(false)
    onLogout()
  }

  const displayName = user.firstName && user.lastName ? `${user.firstName} ${user.lastName}` : user.username

  const initials =
    user.firstName && user.lastName
      ? `${user.firstName[0]}${user.lastName[0]}`
      : user.username.slice(0, 2).toUpperCase()

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant="ghost"
        className="flex items-center gap-2 px-3 py-2 h-auto hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <div className="w-8 h-8 rounded-full overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center border-2 border-gray-200 dark:border-gray-600">
          {user.profilePicture ? (
            <img
              src={user.profilePicture || "/placeholder.svg"}
              alt={displayName}
              className="w-full h-full object-cover"
            />
          ) : (
            <User className="w-5 h-5 text-white" />
          )}
        </div>
        <span className="hidden sm:block text-sm font-medium text-gray-700 dark:text-gray-200">{displayName}</span>
        <ChevronDown
          className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
        />
      </Button>

      {isOpen && (
        <Card className="absolute right-0 top-full mt-2 w-56 shadow-lg border border-gray-200 dark:border-gray-700 z-50 animate-in slide-in-from-top-2 duration-200">
          <CardContent className="p-0">
            <div className="py-2">
              {/* User Info Header */}
              <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center border-2 border-gray-200 dark:border-gray-600">
                    {user.profilePicture ? (
                      <img
                        src={user.profilePicture || "/placeholder.svg"}
                        alt={displayName}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User className="w-6 h-6 text-white" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{displayName}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
                  </div>
                </div>
              </div>

              {/* Menu Items */}
              <div className="py-1">
                <button
                  onClick={handleProfileClick}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-150"
                >
                  <Settings className="w-4 h-4" />
                  <span>Profile/settings</span>
                </button>

                <button
                  onClick={handleWatchlistClick}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-150"
                >
                  <List className="w-4 h-4" />
                  <span>Watchlist</span>
                </button>

                <div className="border-t border-gray-100 dark:border-gray-700 my-1"></div>

                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors duration-150"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Log out</span>
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
