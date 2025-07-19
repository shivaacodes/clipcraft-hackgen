import { v2 as cloudinary } from 'cloudinary';

// Configure Cloudinary
cloudinary.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET,
});

export interface CloudinaryUploadResult {
  public_id: string;
  version: number;
  format: string;
  resource_type: string;
  bytes: number;
  width?: number;
  height?: number;
  duration?: number;
  url: string;
  secure_url: string;
  thumbnail_url?: string;
  created_at: string;
}

export interface UploadOptions {
  folder?: string;
  public_id?: string;
  resource_type?: 'image' | 'video' | 'raw' | 'auto';
  transformation?: any[];
  eager?: any[];
  quality?: string | number;
  format?: string;
}

/**
 * Upload a file buffer to Cloudinary
 */
export async function uploadToCloudinary(
  buffer: Buffer,
  options: UploadOptions = {}
): Promise<CloudinaryUploadResult> {
  return new Promise((resolve, reject) => {
    const defaultOptions: UploadOptions = {
      folder: 'titan-uploads',
      resource_type: 'auto',
      quality: 'auto',
      ...options,
    };

    cloudinary.uploader.upload_stream(
      defaultOptions,
      (error, result) => {
        if (error) {
          reject(error);
        } else if (result) {
          resolve(result as CloudinaryUploadResult);
        } else {
          reject(new Error('Upload failed - no result returned'));
        }
      }
    ).end(buffer);
  });
}

/**
 * Upload a video file with thumbnail generation
 */
export async function uploadVideoWithThumbnail(
  buffer: Buffer,
  filename: string,
  userId: string
): Promise<{
  video: CloudinaryUploadResult;
  thumbnail: CloudinaryUploadResult;
}> {
  const timestamp = Date.now();
  const publicId = `${userId}_${timestamp}`;
  
  // Upload video with eager transformation for thumbnail
  const videoResult = await uploadToCloudinary(buffer, {
    folder: 'titan-uploads/videos',
    public_id: publicId,
    resource_type: 'video',
    eager: [
      {
        width: 320,
        height: 240,
        crop: 'fill',
        quality: 'auto',
        format: 'jpg',
        start_offset: '1s' // Generate thumbnail at 1 second
      }
    ]
  });

  // Extract thumbnail URL from eager transformation
  const thumbnailUrl = videoResult.eager?.[0]?.secure_url;
  
  // Create thumbnail result object
  const thumbnailResult: CloudinaryUploadResult = {
    public_id: `${publicId}_thumbnail`,
    version: videoResult.version,
    format: 'jpg',
    resource_type: 'image',
    bytes: 0, // Cloudinary doesn't return bytes for eager transformations
    width: 320,
    height: 240,
    url: thumbnailUrl || '',
    secure_url: thumbnailUrl || '',
    created_at: videoResult.created_at,
  };

  return {
    video: videoResult,
    thumbnail: thumbnailResult
  };
}

/**
 * Delete a file from Cloudinary
 */
export async function deleteFromCloudinary(
  publicId: string,
  resourceType: 'image' | 'video' | 'raw' = 'image'
): Promise<any> {
  return cloudinary.uploader.destroy(publicId, {
    resource_type: resourceType
  });
}

/**
 * Generate a transformation URL for an existing Cloudinary asset
 */
export function generateTransformationUrl(
  publicId: string,
  transformations: any[] = [],
  options: {
    resourceType?: 'image' | 'video';
    format?: string;
    quality?: string | number;
  } = {}
): string {
  return cloudinary.url(publicId, {
    resource_type: options.resourceType || 'image',
    format: options.format,
    quality: options.quality || 'auto',
    transformation: transformations,
    secure: true,
  });
}

/**
 * Get video thumbnail URL
 */
export function getVideoThumbnailUrl(
  publicId: string,
  options: {
    width?: number;
    height?: number;
    quality?: string | number;
  } = {}
): string {
  return generateTransformationUrl(publicId, [
    {
      width: options.width || 320,
      height: options.height || 240,
      crop: 'fill',
      start_offset: '1s'
    }
  ], {
    resourceType: 'video',
    format: 'jpg',
    quality: options.quality || 'auto'
  });
}

/**
 * Validate Cloudinary configuration
 */
export function validateCloudinaryConfig(): boolean {
  const { cloud_name, api_key, api_secret } = cloudinary.config();
  
  if (!cloud_name || !api_key || !api_secret) {
    console.error('Cloudinary configuration is incomplete. Please check your environment variables:');
    console.error('- CLOUDINARY_CLOUD_NAME');
    console.error('- CLOUDINARY_API_KEY'); 
    console.error('- CLOUDINARY_API_SECRET');
    return false;
  }
  
  return true;
}

export default cloudinary;