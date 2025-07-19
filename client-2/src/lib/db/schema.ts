import { pgTable, text, timestamp, boolean, integer} from "drizzle-orm/pg-core";

export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").notNull(),
  image: text("image"),
  createdAt: timestamp("created_at").notNull(),
  updatedAt: timestamp("updated_at").notNull(),
});

export const session = pgTable("session", {
  id: text("id").primaryKey(),
  expiresAt: timestamp("expires_at").notNull(),
  token: text("token").notNull().unique(),
  createdAt: timestamp("created_at").notNull(),
  updatedAt: timestamp("updated_at").notNull(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
});

export const account = pgTable("account", {
  id: text("id").primaryKey(),
  accountId: text("account_id").notNull(),
  providerId: text("provider_id").notNull(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  idToken: text("id_token"),
  accessTokenExpiresAt: timestamp("access_token_expires_at"),
  refreshTokenExpiresAt: timestamp("refresh_token_expires_at"),
  scope: text("scope"),
  password: text("password"),
  createdAt: timestamp("created_at").notNull(),
  updatedAt: timestamp("updated_at").notNull(),
});

export const verification = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expires_at").notNull(),
  createdAt: timestamp("created_at"),
  updatedAt: timestamp("updated_at"),
});

export const videos = pgTable("videos", {
  id: text("id").primaryKey(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  title: text("title").notNull(),
  description: text("description"),
  fileUrl: text("file_url").notNull(),
  cloudinaryPublicId: text("cloudinary_public_id"), // Cloudinary public ID for management
  durationSeconds: integer("duration_seconds"),
  uploadedAt: timestamp("uploaded_at").notNull(),
});

export const transcripts = pgTable("transcripts", {
  id: text("id").primaryKey(),
  videoId: text("video_id")
    .notNull()
    .references(() => videos.id, { onDelete: "cascade" }),
  fullText: text("full_text").notNull(),
  createdAt: timestamp("created_at").notNull(),
});

export const transcriptChunks = pgTable("transcript_chunks", {
  id: text("id").primaryKey(),
  transcriptId: text("transcript_id")
    .notNull()
    .references(() => transcripts.id, { onDelete: "cascade" }),
  startTime: integer("start_time").notNull(), // in seconds
  endTime: integer("end_time").notNull(),
  text: text("text").notNull(),
  mood: text("mood"), // e.g., "tense", "romantic"
  genre: text("genre"), // e.g., "thriller", "comedy"
  audienceAge: text("audience_age"), // e.g., "teens", "adults"
});

export const clips = pgTable("clips", {
  id: text("id").primaryKey(),
  videoId: text("video_id")
    .notNull()
    .references(() => videos.id, { onDelete: "cascade" }),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  title: text("title"),
  audienceTarget: text("audience_target"), // e.g. "young adults who like drama"
  clipUrl: text("clip_url").notNull(),
  clipCloudinaryId: text("clip_cloudinary_id"), // Cloudinary public ID for clip
  durationSeconds: integer("duration_seconds"),
  exportedFormat: text("exported_format"), // e.g., "reel", "status", "short"
  createdAt: timestamp("created_at").notNull(),
});

export const bgmTemplates = pgTable("bgm_templates", {
  id: text("id").primaryKey(),
  name: text("name").notNull(), // e.g., "Melancholy Piano"
  mood: text("mood").notNull(), // e.g., "emotional", "suspense"
  audioUrl: text("audio_url").notNull(),
  createdAt: timestamp("created_at").notNull(),
});

export const projects = pgTable("projects", {
  id: text("id").primaryKey(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  name: text("name").notNull(),
  description: text("description"),
  thumbnailUrl: text("thumbnail_url"),
  thumbnailCloudinaryId: text("thumbnail_cloudinary_id"), // Cloudinary public ID for thumbnail
  videoUrl: text("video_url"), // Cloudinary video URL
  videoCloudinaryId: text("video_cloudinary_id"), // Cloudinary public ID for video
  type: text("type"), // e.g., "Travel", "Business", "Personal"
  language: text("language"), // e.g., "English", "Hindi", "Tamil"
  genre: text("genre"), // e.g., "Comedy", "Drama", "Action"
  durationSeconds: integer("duration_seconds"),
  createdAt: timestamp("created_at").notNull(),
  updatedAt: timestamp("updated_at").notNull(),
});
