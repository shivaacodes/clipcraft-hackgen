import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { uploadVideoWithThumbnail, validateCloudinaryConfig } from "@/lib/cloudinary";

export async function POST(request: NextRequest) {
  try {
    // Validate Cloudinary configuration
    if (!validateCloudinaryConfig()) {
      return NextResponse.json(
        { error: "Cloudinary configuration is incomplete" },
        { status: 500 }
      );
    }

    const session = await auth.api.getSession({
      headers: await headers(),
    });

    if (!session) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const formData = await request.formData();
    const file = formData.get("video") as File;
    
    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    // Validate file type
    const validTypes = ["video/mp4", "video/mov", "video/avi", "video/mkv", "video/webm"];
    if (!validTypes.includes(file.type)) {
      return NextResponse.json(
        { error: "Invalid file type. Only video files are allowed." },
        { status: 400 }
      );
    }

    // Validate file size (100MB limit)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: "File too large. Maximum size is 100MB." },
        { status: 400 }
      );
    }

    // Convert file to buffer
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Upload to Cloudinary with thumbnail generation
    const { video, thumbnail } = await uploadVideoWithThumbnail(
      buffer,
      file.name,
      session.user.id
    );

    return NextResponse.json({
      success: true,
      videoUrl: video.secure_url,
      thumbnailUrl: thumbnail.secure_url,
      filename: video.public_id,
      originalName: file.name,
      size: file.size,
      cloudinary: {
        videoPublicId: video.public_id,
        thumbnailPublicId: thumbnail.public_id,
        videoFormat: video.format,
        duration: video.duration,
        width: video.width,
        height: video.height,
      },
    });

  } catch (error) {
    console.error("Upload error:", error);
    
    // Handle Cloudinary specific errors
    if (error && typeof error === 'object' && 'http_code' in error) {
      const cloudinaryError = error as any;
      return NextResponse.json(
        { 
          error: `Cloudinary upload failed: ${cloudinaryError.message || 'Unknown error'}`,
          details: cloudinaryError.error?.message || 'Please check your Cloudinary configuration'
        },
        { status: cloudinaryError.http_code || 500 }
      );
    }
    
    return NextResponse.json(
      { error: "Failed to upload file" },
      { status: 500 }
    );
  }
}