import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Edit, Mail, Calendar, User, Shield, Bell, Key, ChevronLeft } from "lucide-react"
import { ProfilePictureUpload } from "../components/ProfilePictureUpload"
import { EditProfileModal } from "../components/EditProfileModal"
import { PreferencesModal } from "../components/PreferencesModal"
import { ChangePasswordModal } from "../components/ChangePasswordModal"
import { useTheme } from "@/components/theme-provider"
import type { UserProfile, EditProfileData } from "../types/index"
import { useNavigate } from "react-router-dom"
import { authApi } from "../api/authApi"

export default function ProfilePage() {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isPreferencesModalOpen, setIsPreferencesModalOpen] = useState(false)
  const [isChangePasswordModalOpen, setIsChangePasswordModalOpen] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [textScale, setTextScale] = useState(1)
  const textContainerRef = useRef<HTMLDivElement>(null)
  const { setTheme, isDark } = useTheme()
  const navigate = useNavigate()

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await authApi.fetchUserProfile()
        setUserProfile({
          ...data,
          preferences: {
            darkMode: false,
            emailNotifications: true,
            pushNotifications: false,
          },
        })
      } catch (err) {
        // handle error
      }
    }
    fetchProfile()
  }, [])

  // Dynamic text sizing logic
  useEffect(() => {
    const adjustTextSize = () => {
      if (textContainerRef.current) {
        const container = textContainerRef.current
        const containerWidth = container.offsetWidth
        const containerHeight = container.offsetHeight

        // Reset scale to measure natural size
        setTextScale(1)

        setTimeout(() => {
          const textHeight = container.scrollHeight
          const textWidth = container.scrollWidth

          let scale = 1

          // Adjust scale based on container constraints
          if (textHeight > containerHeight) {
            scale = Math.min(scale, (containerHeight / textHeight) * 0.9)
          }

          if (textWidth > containerWidth) {
            scale = Math.min(scale, (containerWidth / textWidth) * 0.9)
          }

          // Minimum scale to maintain readability
          scale = Math.max(scale, 0.75)

          setTextScale(scale)
        }, 10)
      }
    }

    adjustTextSize()
    window.addEventListener("resize", adjustTextSize)

    return () => window.removeEventListener("resize", adjustTextSize)
  }, [userProfile?.firstName, userProfile?.lastName, userProfile?.username, userProfile?.email])

  const handleProfilePictureChange = (file: File) => {
    console.log("Profile picture changed:", file)
  }

  const handleEditProfile = async (data: EditProfileData) => {
    try {
      const updated = await authApi.updateUserProfile(data)
      setUserProfile((prev: UserProfile | null) => prev ? { ...prev, ...updated } : updated)
    } catch (err) {
      // handle error
    }
  }

  const handlePreferencesChange = (preferences: UserProfile["preferences"]) => {
    setUserProfile((prev: UserProfile | null) => prev ? { ...prev, preferences: {
      darkMode: preferences.darkMode ?? false,
      emailNotifications: preferences.emailNotifications ?? true,
      pushNotifications: preferences.pushNotifications ?? false,
    } } : prev)
    setTheme(preferences.darkMode ? "dark" : "light")
  }

  const handlePasswordChange = (currentPassword: string, newPassword: string) => {
    console.log("Password change requested")
  }

  const handleNotificationToggle = (type: keyof UserProfile["preferences"]) => {
    const newPreferences = {
      darkMode: userProfile?.preferences.darkMode ?? false,
      emailNotifications: userProfile?.preferences.emailNotifications ?? true,
      pushNotifications: userProfile?.preferences.pushNotifications ?? false,
      [type]: !userProfile?.preferences?.[type],
    }
    setUserProfile((prev: UserProfile | null) => prev ? { ...prev, preferences: newPreferences } : prev)
    if (type === "darkMode") {
      setTheme(newPreferences.darkMode ? "dark" : "light")
    }
  }

  const formatJoinDate = (dateString: string) => {
    if (!dateString) return ""
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  const handleBack = () => {
    if (localStorage.getItem('user')) {
      const user = JSON.parse(localStorage.getItem('user'));
      navigate(`/landing/${user.id}`);
    } else {
      navigate('/landing');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4 md:p-6 transition-colors duration-300">
      <button
        onClick={handleBack}
        className="flex items-center gap-2 mb-4 px-3 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        aria-label="Back to landing page"
      >
        <ChevronLeft className="w-5 h-5" />
        <span>Back</span>
      </button>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header Card */}
        <Card className="overflow-hidden dark:bg-gray-800 dark:border-gray-700 transition-colors duration-300">
          <div className="h-32 bg-gradient-to-r from-blue-500 to-purple-600"></div>
          <CardContent className="relative pt-6 pb-6">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div className="flex flex-col md:flex-row md:items-start gap-4 md:gap-6">
                <div className="flex justify-center md:justify-start -mt-20 md:-mt-20">
                  <ProfilePictureUpload
                    currentPicture={userProfile?.profilePicture}
                    onPictureChange={handleProfilePictureChange}
                    isEditing={isEditing}
                  />
                </div>
                <div
                  ref={textContainerRef}
                  className="text-center md:text-left flex-1 min-w-0 pt-2"
                  style={{ transform: `scale(${textScale})`, transformOrigin: "center top" }}
                >
                  <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white leading-tight mb-1 transition-colors duration-300">
                    {userProfile?.firstName && userProfile?.lastName
                      ? `${userProfile.firstName} ${userProfile.lastName}`
                      : userProfile?.username}
                  </h1>
                  <p className="text-gray-600 dark:text-gray-300 mb-2 transition-colors duration-300">
                    @{userProfile?.username}
                  </p>
                  <div className="flex items-center justify-center md:justify-start gap-2">
                    <Mail className="w-4 h-4 text-gray-500 dark:text-gray-400 transition-colors duration-300" />
                    <span className="text-sm text-gray-600 dark:text-gray-300 transition-colors duration-300">
                      {userProfile?.email}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2 justify-center md:justify-end pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsEditModalOpen(true)}
                  className="flex items-center gap-2 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700 transition-colors duration-300"
                >
                  <Edit className="w-4 h-4" />
                  Edit Profile
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700 transition-colors duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 dark:text-white transition-colors duration-300">
                  <User className="w-5 h-5" />
                  About
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed transition-colors duration-300">
                  {userProfile?.bio || "No bio available."}
                </p>
                <div className="flex items-center gap-2 mt-4 text-sm text-gray-600 dark:text-gray-400 transition-colors duration-300">
                  <Calendar className="w-4 h-4" />
                  <span>Joined {formatJoinDate(String(userProfile?.joinedDate || ""))}</span>
                </div>
              </CardContent>
            </Card>

            {/* Account Status */}
            <Card className="dark:bg-gray-800 dark:border-gray-700 transition-colors duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 dark:text-white transition-colors duration-300">
                  <Shield className="w-5 h-5" />
                  Account Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium dark:text-gray-300 transition-colors duration-300">
                      Account Type
                    </span>
                    <Badge variant="secondary" className="dark:bg-gray-700 dark:text-gray-200">
                      Premium
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium dark:text-gray-300 transition-colors duration-300">
                      Email Verified
                    </span>
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      Verified
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="dark:bg-gray-800 dark:border-gray-700 transition-colors duration-300">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg dark:text-white transition-colors duration-300">
                  <Bell className="w-5 h-5" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm dark:text-gray-300 transition-colors duration-300">Email Notifications</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-0 dark:hover:bg-gray-700 transition-colors duration-300"
                    onClick={() => handleNotificationToggle("emailNotifications")}
                  >
                    <Badge
                      variant={userProfile?.preferences.emailNotifications ? "default" : "secondary"}
                      className="cursor-pointer hover:opacity-80 transition-opacity dark:bg-gray-700 dark:text-gray-200"
                    >
                      {userProfile?.preferences.emailNotifications ? "On" : "Off"}
                    </Badge>
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm dark:text-gray-300 transition-colors duration-300">Push Notifications</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-0 dark:hover:bg-gray-700 transition-colors duration-300"
                    onClick={() => handleNotificationToggle("pushNotifications")}
                  >
                    <Badge
                      variant={userProfile?.preferences.pushNotifications ? "default" : "secondary"}
                      className="cursor-pointer hover:opacity-80 transition-opacity dark:bg-gray-700 dark:text-gray-200"
                    >
                      {userProfile?.preferences.pushNotifications ? "On" : "Off"}
                    </Badge>
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm dark:text-gray-300 transition-colors duration-300">Dark Mode</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-0 dark:hover:bg-gray-700 transition-colors duration-300"
                    onClick={() => handleNotificationToggle("darkMode")}
                  >
                    <Badge
                      variant={userProfile?.preferences.darkMode ? "default" : "secondary"}
                      className="cursor-pointer hover:opacity-80 transition-opacity dark:bg-gray-700 dark:text-gray-200"
                    >
                      {userProfile?.preferences.darkMode ? "On" : "Off"}
                    </Badge>
                  </Button>
                </div>

                <div className="pt-2 border-t border-gray-200 dark:border-gray-600">
                  <Button
                    variant="outline"
                    className="w-full justify-start dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700 transition-colors duration-300"
                    onClick={() => setIsChangePasswordModalOpen(true)}
                  >
                    <Key className="w-4 h-4 mr-2" />
                    Change Password
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Modals */}
      <EditProfileModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onSave={handleEditProfile}
        initialData={{
          username: userProfile?.username || "",
          firstName: userProfile?.firstName || "",
          lastName: userProfile?.lastName || "",
          bio: userProfile?.bio || "",
        }}
      />

      <PreferencesModal
        isOpen={isPreferencesModalOpen}
        onClose={() => setIsPreferencesModalOpen(false)}
        onSave={handlePreferencesChange}
        initialPreferences={userProfile?.preferences || {
          darkMode: false,
          emailNotifications: true,
          pushNotifications: false,
        }}
      />

      <ChangePasswordModal
        isOpen={isChangePasswordModalOpen}
        onClose={() => setIsChangePasswordModalOpen(false)}
        onSave={handlePasswordChange}
      />
    </div>
  )
}
