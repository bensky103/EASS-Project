"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Camera, User } from "lucide-react"

interface ProfilePictureUploadProps {
  currentPicture?: string
  onPictureChange: (file: File) => void
  isEditing: boolean
}

export function ProfilePictureUpload({ currentPicture, onPictureChange, isEditing }: ProfilePictureUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(currentPicture || null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      onPictureChange(file)
    }
  }

  const triggerFileSelect = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="relative">
      <div className="w-32 h-32 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-700 border-4 border-white dark:border-gray-600 shadow-lg transition-colors duration-300">
        {previewUrl ? (
          <img src={previewUrl || "/placeholder.svg"} alt="Profile" className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-400 to-purple-500 dark:from-blue-600 dark:to-purple-700 transition-colors duration-300">
            <User className="w-16 h-16 text-white" />
          </div>
        )}
      </div>

      {isEditing && (
        <>
          <Button
            type="button"
            size="sm"
            className="absolute -bottom-2 -right-2 rounded-full w-10 h-10 p-0 shadow-lg dark:bg-gray-700 dark:hover:bg-gray-600 dark:border-gray-600 transition-colors duration-300"
            onClick={triggerFileSelect}
          >
            <Camera className="w-4 h-4" />
          </Button>
          <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />
        </>
      )}
    </div>
  )
}
