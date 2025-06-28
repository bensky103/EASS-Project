"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { X } from "lucide-react"

interface PreferencesData {
  darkMode: boolean
  emailNotifications: boolean
  pushNotifications: boolean
}

interface PreferencesModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (preferences: PreferencesData) => void
  initialPreferences: PreferencesData
}

export function PreferencesModal({ isOpen, onClose, onSave, initialPreferences }: PreferencesModalProps) {
  const [preferences, setPreferences] = useState<PreferencesData>(initialPreferences)

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(preferences)
    onClose()
  }

  const handleToggle = (key: keyof PreferencesData) => {
    setPreferences((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70 flex items-center justify-center z-50 p-4 transition-colors duration-300">
      <Card className="w-full max-w-md dark:bg-gray-800 dark:border-gray-700 transition-colors duration-300">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="dark:text-white transition-colors duration-300">Preferences</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0">
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label
                  htmlFor="darkMode"
                  className="text-sm font-medium dark:text-gray-200 transition-colors duration-300"
                >
                  Dark Mode
                </Label>
                <Switch id="darkMode" checked={preferences.darkMode} onCheckedChange={() => handleToggle("darkMode")} />
              </div>

              <div className="flex items-center justify-between">
                <Label
                  htmlFor="emailNotifications"
                  className="text-sm font-medium dark:text-gray-200 transition-colors duration-300"
                >
                  Email Notifications
                </Label>
                <Switch
                  id="emailNotifications"
                  checked={preferences.emailNotifications}
                  onCheckedChange={() => handleToggle("emailNotifications")}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label
                  htmlFor="pushNotifications"
                  className="text-sm font-medium dark:text-gray-200 transition-colors duration-300"
                >
                  Push Notifications
                </Label>
                <Switch
                  id="pushNotifications"
                  checked={preferences.pushNotifications}
                  onCheckedChange={() => handleToggle("pushNotifications")}
                />
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                type="submit"
                className="flex-1 dark:bg-blue-600 dark:hover:bg-blue-700 transition-colors duration-300"
              >
                Save Preferences
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className="dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700 transition-colors duration-300"
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
