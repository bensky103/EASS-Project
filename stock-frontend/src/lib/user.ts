import { ObjectId } from "mongodb"
import { getDatabase } from "../mongodb"
import bcrypt from "bcryptjs"

export interface User {
  _id?: ObjectId
  username: string
  email: string
  password: string
  firstName?: string
  lastName?: string
  createdAt: Date
  updatedAt: Date
}

export class UserModel {
  static async create(userData: Omit<User, "_id" | "createdAt" | "updatedAt">): Promise<User> {
    const db = await getDatabase()
    const users = db.collection<User>("users")

    // Check if username or email already exists
    const existingUser = await users.findOne({
      $or: [{ username: userData.username }, { email: userData.email }],
    })

    if (existingUser) {
      if (existingUser.username === userData.username) {
        throw new Error("Username already exists")
      }
      if (existingUser.email === userData.email) {
        throw new Error("Email already exists")
      }
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(userData.password, 12)

    const newUser: Omit<User, "_id"> = {
      ...userData,
      password: hashedPassword,
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    const result = await users.insertOne(newUser)
    const user = await users.findOne({ _id: result.insertedId })

    if (!user) {
      throw new Error("Failed to create user")
    }

    return user
  }

  static async findByIdentifier(identifier: string): Promise<User | null> {
    const db = await getDatabase()
    const users = db.collection<User>("users")

    // Find by username or email
    return await users.findOne({
      $or: [{ username: identifier }, { email: identifier }],
    })
  }

  static async findById(id: string): Promise<User | null> {
    const db = await getDatabase()
    const users = db.collection<User>("users")

    return await users.findOne({ _id: new ObjectId(id) })
  }

  static async updatePassword(id: string, newPassword: string): Promise<boolean> {
    const db = await getDatabase()
    const users = db.collection<User>("users")

    const hashedPassword = await bcrypt.hash(newPassword, 12)

    const result = await users.updateOne(
      { _id: new ObjectId(id) },
      {
        $set: {
          password: hashedPassword,
          updatedAt: new Date(),
        },
      },
    )

    return result.modifiedCount > 0
  }

  static async verifyPassword(plainPassword: string, hashedPassword: string): Promise<boolean> {
    return await bcrypt.compare(plainPassword, hashedPassword)
  }
}
