ALTER TABLE "clips" ADD COLUMN "clip_cloudinary_id" text;--> statement-breakpoint
ALTER TABLE "projects" ADD COLUMN "thumbnail_cloudinary_id" text;--> statement-breakpoint
ALTER TABLE "videos" ADD COLUMN "cloudinary_public_id" text;