# Cloudinary Integration Setup Guide

This guide explains how to set up and configure Cloudinary for video uploads in your Titan application.

## Overview

The application has been successfully migrated from local file storage to Cloudinary cloud storage. This provides:

- **Scalable Storage**: No more local disk space limitations
- **Automatic Optimization**: Built-in video compression and format optimization  
- **Global CDN**: Fast video delivery worldwide
- **Thumbnail Generation**: Automatic thumbnail creation without FFmpeg
- **Transformation API**: On-the-fly video transformations

## Prerequisites

1. **Cloudinary Account**: Sign up at [cloudinary.com](https://cloudinary.com)
2. **API Credentials**: Get your Cloud Name, API Key, and API Secret from your dashboard

## Configuration Steps

### 1. Set Environment Variables

Update your `.env` file with your Cloudinary credentials:

```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key  
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### 2. Install Dependencies

The required Cloudinary SDK has been installed:

```bash
bun install cloudinary
```

### 3. Database Migration

Run the database migration to add Cloudinary fields:

```bash
bun run db:generate
bun run db:migrate
```

## Architecture Changes

### Frontend Upload Flow

1. **File Selection**: User selects video file (same as before)
2. **Client Validation**: File type and size validation (same as before)  
3. **Upload to Cloudinary**: Direct upload to Cloudinary via `/api/upload`
4. **Thumbnail Generation**: Automatic thumbnail at 1-second mark
5. **Database Storage**: Cloudinary URLs and metadata saved

### Backend Processing

1. **Cloudinary Integration**: New Python endpoint for processing Cloudinary videos
2. **Download & Process**: Videos downloaded from Cloudinary for transcription
3. **Cleanup**: Temporary files cleaned up after processing

## New API Endpoints

### Upload API (`/api/upload`)
- **Method**: POST
- **Input**: FormData with video file
- **Output**: Cloudinary URLs and metadata
- **Features**: 
  - Automatic thumbnail generation
  - File validation
  - Cloudinary public ID management

### Python Processing API (`/api/v1/process/process-cloudinary-video`)
- **Method**: POST  
- **Input**: JSON with video URL
- **Output**: Job ID for tracking
- **Features**:
  - Downloads from Cloudinary
  - Transcription and vibe analysis
  - Progress tracking

## File Structure

```
src/
├── lib/
│   └── cloudinary.ts          # Cloudinary configuration and utilities
├── types/
│   └── cloudinary.ts          # TypeScript interfaces
└── app/api/upload/
    └── route.ts               # Updated upload endpoint

server/
└── app/routes/
    └── process.py             # Updated with Cloudinary support
```

## Usage Examples

### Basic Upload

```typescript
// Frontend upload (automatic with existing code)
const formData = new FormData();
formData.append('video', videoFile);

const response = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
// result.videoUrl - Cloudinary video URL
// result.thumbnailUrl - Cloudinary thumbnail URL
```

### Processing Cloudinary Video

```python
# Process video from Cloudinary URL
import requests

response = requests.post('/api/v1/process/process-cloudinary-video', json={
    'video_url': 'https://res.cloudinary.com/your-cloud/video/upload/...',
    'chunk_strategy': 'adaptive',
    'include_vibe_analysis': True
})

job_id = response.json()['job_id']
```

### Generating Transformations

```typescript
import { generateTransformationUrl, getVideoThumbnailUrl } from '@/lib/cloudinary';

// Custom thumbnail
const thumbnailUrl = getVideoThumbnailUrl('video_public_id', {
  width: 640,
  height: 480,
  quality: 'auto:best'
});

// Custom video transformation
const optimizedUrl = generateTransformationUrl('video_public_id', [
  { width: 720, height: 480, crop: 'fill' },
  { quality: 'auto:good', format: 'mp4' }
], { resourceType: 'video' });
```

## Migration from Local Storage

### Existing Files
- Local files in `public/uploads/` can be migrated manually
- Database URLs need to be updated to Cloudinary URLs
- Consider a migration script for bulk operations

### Database Schema
New fields added:
- `videos.cloudinaryPublicId` - For video management
- `projects.thumbnailCloudinaryId` - For thumbnail management  
- `clips.clipCloudinaryId` - For clip management

## Troubleshooting

### Configuration Issues
```bash
# Check configuration
bun run dev
# Look for "Cloudinary configuration is incomplete" errors
```

### Upload Failures
- Verify API credentials are correct
- Check file size limits (100MB default)
- Ensure valid video formats (MP4, MOV, AVI, MKV, WebM)

### Processing Issues
- Verify Python server can access Cloudinary URLs
- Check network connectivity
- Monitor server logs for download errors

## Performance Considerations

### Upload Performance
- Cloudinary uploads may be slower than local storage initially
- Consider implementing upload progress indicators
- Use Cloudinary's direct upload for large files

### Processing Performance  
- Downloads from Cloudinary add network latency
- Consider caching frequently accessed videos
- Monitor bandwidth usage

## Security

### API Key Management
- Never expose API secrets in frontend code
- Use environment variables for all credentials
- Rotate API keys regularly

### Access Control
- Cloudinary URLs are publicly accessible by default
- Consider using authenticated URLs for sensitive content
- Implement proper user authorization

## Monitoring

### Cloudinary Dashboard
- Monitor usage statistics
- Track bandwidth consumption
- Review transformation usage

### Application Metrics
- Upload success/failure rates
- Processing times
- Error rates

## Cost Optimization

### Storage
- Set up auto-deletion policies for old files
- Use appropriate quality settings
- Monitor storage usage

### Bandwidth
- Enable auto-optimization
- Use appropriate formats (WebP for images, MP4 for videos)
- Implement caching strategies

## Next Steps

1. **Test thoroughly** with various video formats and sizes
2. **Monitor** Cloudinary usage and costs
3. **Optimize** transformation settings for your use case
4. **Implement** cleanup policies for old uploads
5. **Consider** implementing direct upload from frontend

## Support

For issues:
1. Check Cloudinary documentation: [cloudinary.com/documentation](https://cloudinary.com/documentation)
2. Review application logs for specific errors
3. Test with Cloudinary's API explorer tool